from rest_framework import serializers
from django.utils import timezone
from .models import Payment, Invoice

class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for payments"""
    
    user_name = serializers.ReadOnlyField(source='user.get_full_name')
    booking_details = serializers.SerializerMethodField()
    
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ('user', 'transaction_id', 'status', 'created_at', 'updated_at')
    
    def get_booking_details(self, obj):
        """Get basic booking information"""
        if not obj.booking:
            return None
        
        booking = obj.booking
        return {
            'id': booking.id,
            'car': f"{booking.car.model.brand.name} {booking.car.model.name}",
            'license_plate': booking.car.license_plate,
            'start_time': booking.start_time,
            'end_time': booking.end_time,
            'status': booking.status
        }

class InvoiceSerializer(serializers.ModelSerializer):
    """Serializer for invoices"""
    
    user_name = serializers.ReadOnlyField(source='user.get_full_name')
    is_overdue = serializers.SerializerMethodField()
    payment_details = serializers.SerializerMethodField()
    
    class Meta:
        model = Invoice
        fields = '__all__'
        read_only_fields = ('user', 'payment', 'created_at', 'updated_at')
    
    def get_is_overdue(self, obj):
        """Check if the invoice is overdue"""
        return obj.status == 'pending' and obj.due_date < timezone.now()
    
    def get_payment_details(self, obj):
        """Get payment information if it exists"""
        if not obj.payment:
            return None
        
        return {
            'id': obj.payment.id,
            'amount': obj.payment.amount,
            'status': obj.payment.status,
            'payment_method': obj.payment.payment_method,
            'transaction_id': obj.payment.transaction_id,
            'created_at': obj.payment.created_at
        }

class PaymentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating payments"""
    
    class Meta:
        model = Payment
        fields = ('booking', 'amount', 'payment_type', 'payment_method', 'description')
    
    def validate(self, data):
        """Additional validation when creating a payment"""
        
        # Check booking if specified
        booking = data.get('booking')
        if booking:
            # Check that the user can pay for this booking
            user = self.context['request'].user
            if booking.user != user and not user.is_staff:
                raise serializers.ValidationError(
                    {"booking": "You cannot pay for someone else's bookings"}
                )
            
            # Check booking status
            if booking.status not in ['pending', 'confirmed']:
                raise serializers.ValidationError(
                    {"booking": "Only pending or confirmed bookings can be paid"}
                )
        
        return data
    
    def create(self, validated_data):
        # Add the current user to the payment
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
