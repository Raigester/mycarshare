from rest_framework import serializers
from django.utils import timezone
from .models import Booking, BookingHistory
from cars.models import Car

class BookingSerializer(serializers.ModelSerializer):
    """Serializer for bookings"""
    
    car_details = serializers.SerializerMethodField()
    user_name = serializers.ReadOnlyField(source='user.get_full_name')
    duration_hours = serializers.SerializerMethodField()
    
    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ('user', 'total_price', 'status', 'created_at', 'updated_at')
    
    def get_car_details(self, obj):
        """Get basic car information"""
        car = obj.car
        return {
            'id': car.id,
            'brand': car.model.brand.name,
            'model': car.model.name,
            'license_plate': car.license_plate,
            'main_photo': car.main_photo.url if car.main_photo else None
        }
    
    def get_duration_hours(self, obj):
        """Calculate booking duration in hours"""
        duration = obj.end_time - obj.start_time
        hours = duration.total_seconds() / 3600
        return round(hours, 1)
    
    def validate(self, data):
        """Additional data validation"""
        
        # Check car availability
        car = data.get('car')
        if car and car.status not in ['available']:
            raise serializers.ValidationError({"car": "The car is not available for booking"})
        
        # Check time validity
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        
        if start_time and end_time:
            # Ensure start time is before end time
            if start_time >= end_time:
                raise serializers.ValidationError({"end_time": "End time must be later than start time"})
            
            # Ensure start time is in the future
            if start_time <= timezone.now():
                raise serializers.ValidationError({"start_time": "Start time must be in the future"})
            
            # Check minimum duration (e.g., 1 hour)
            min_duration = timezone.timedelta(hours=1)
            if end_time - start_time < min_duration:
                raise serializers.ValidationError(
                    {"end_time": "The minimum booking duration is 1 hour"}
                )
            
            # Check for overlapping bookings
            if car:
                booking_id = self.instance.id if self.instance else None
                overlapping_bookings = Booking.objects.exclude(id=booking_id).filter(
                    car=car,
                    status__in=['pending', 'confirmed', 'active'],
                    start_time__lt=end_time,
                    end_time__gt=start_time
                )
                
                if overlapping_bookings.exists():
                    raise serializers.ValidationError(
                        {"car": "The car is already booked for this period"}
                    )
                
                # Calculate preliminary price
                duration = end_time - start_time
                hours = duration.total_seconds() / 3600
                days = hours / 24
                
                # Calculate price by days if duration exceeds 1 day, otherwise by hours
                if days >= 1:
                    total_days = int(days) + (1 if days % 1 > 0 else 0)
                    price = car.price_per_day * total_days
                else:
                    price = car.price_per_hour * hours
                
                # Add option costs
                if data.get('additional_driver'):
                    price += 500  # Example cost for an additional driver
                
                if data.get('baby_seat'):
                    price += 300  # Example cost for a baby seat
                
                # Assign calculated price
                self.context['total_price'] = round(price, 2)
        
        return data
    
    def create(self, validated_data):
        # Add user and calculated price
        validated_data['user'] = self.context['request'].user
        validated_data['total_price'] = self.context.get('total_price', 0)
        
        booking = super().create(validated_data)
        
        # Create a history record
        BookingHistory.objects.create(
            booking=booking,
            status=booking.status,
            notes="Booking created"
        )
        
        return booking
    
    def update(self, instance, validated_data):
        old_status = instance.status
        
        # Recalculate price if dates are updated
        if 'start_time' in validated_data or 'end_time' in validated_data:
            validated_data['total_price'] = self.context.get('total_price', instance.total_price)
        
        # Apply changes
        booking = super().update(instance, validated_data)
        
        # If status changes, create a history record
        if 'status' in validated_data and old_status != booking.status:
            BookingHistory.objects.create(
                booking=booking,
                status=booking.status,
                notes=f"Status changed from {old_status} to {booking.status}"
            )
            
            # Update car status if booking becomes "active" or "completed"
            if booking.status == 'active':
                booking.car.status = 'busy'
                booking.car.save()
            elif booking.status == 'completed' or booking.status == 'cancelled':
                booking.car.status = 'available'
                booking.car.save()
        
        return booking

class BookingHistorySerializer(serializers.ModelSerializer):
    """Serializer for booking history"""
    
    class Meta:
        model = BookingHistory
        fields = '__all__'
