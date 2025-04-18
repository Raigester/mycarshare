from decimal import Decimal
from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import Booking, BookingHistory
from .serializers import BookingSerializer, BookingHistorySerializer
from cars.models import Car

class BookingPermission(permissions.BasePermission):
    """Custom permissions for bookings"""
    
    def has_object_permission(self, request, view, obj):
        # Allow admins to perform any actions
        if request.user.is_staff:
            return True
        
        # Users can view and update only their own bookings
        return obj.user == request.user

class BookingViewSet(viewsets.ModelViewSet):
    """API for bookings"""
    
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated, BookingPermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'car', 'start_time', 'end_time']
    ordering_fields = ['start_time', 'end_time', 'created_at', 'total_price']
    
    def get_queryset(self):
        # Admins see all bookings, regular users see only their own
        user = self.request.user
        if not user or not user.is_authenticated:
            return Booking.objects.none()
        if user.is_staff:
            return Booking.objects.all()
        return Booking.objects.filter(user=user)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a booking"""
        booking = self.get_object()
        
        # Check if cancellation is possible
        if booking.status in ['completed', 'cancelled']:
            return Response(
                {"error": "Cannot cancel a completed or already cancelled booking"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if booking.status == 'active':
            return Response(
                {"error": "Cannot cancel an active booking. Please contact support"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Cancel the booking
        booking.status = 'cancelled'
        booking.save()
        
        # Create a history record
        BookingHistory.objects.create(
            booking=booking,
            status='cancelled',
            notes="Booking cancelled by user"
        )
        
        # Update car status
        car = booking.car
        car.status = 'available'
        car.save()
        
        return Response({"message": "Booking successfully cancelled"})
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def change_status(self, request, pk=None):
        """Change booking status (admin only)"""
        booking = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in [choice[0] for choice in Booking.STATUS_CHOICES]:
            return Response(
                {"error": "Invalid status"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Change booking status
        old_status = booking.status
        booking.status = new_status
        booking.save()
        
        # Create a history record
        BookingHistory.objects.create(
            booking=booking,
            status=new_status,
            notes=f"Status changed from {old_status} to {new_status} by admin"
        )
        
        # Update car status
        car = booking.car
        if new_status == 'active':
            car.status = 'busy'
        elif new_status in ['completed', 'cancelled']:
            car.status = 'available'
        car.save()
        
        return Response({"message": f"Status changed to {new_status}"})
    
    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """Get booking history"""
        booking = self.get_object()
        history = BookingHistory.objects.filter(booking=booking).order_by('-timestamp')
        serializer = BookingHistorySerializer(history, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active bookings"""
        now = timezone.now()
        if request.user.is_staff:
            bookings = Booking.objects.filter(
                status='active',
                start_time__lte=now,
                end_time__gte=now
            )
        else:
            bookings = Booking.objects.filter(
                user=request.user,
                status='active',
                start_time__lte=now,
                end_time__gte=now
            )
        
        serializer = self.get_serializer(bookings, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming bookings"""
        now = timezone.now()
        if request.user.is_staff:
            bookings = Booking.objects.filter(
                status__in=['pending', 'confirmed'],
                start_time__gt=now
            ).order_by('start_time')
        else:
            bookings = Booking.objects.filter(
                user=request.user,
                status__in=['pending', 'confirmed'],
                start_time__gt=now
            ).order_by('start_time')
        
        serializer = self.get_serializer(bookings, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def start_rental(self, request):
        """Start car rental"""
        user = request.user
        car_id = request.data.get('car')
        
        try:
            car = Car.objects.get(id=car_id, status='available')
        except Car.DoesNotExist:
            return Response(
                {"error": "Car not available"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check user's balance
        try:
            balance = user.balance
            min_required = car.price_per_minute * Decimal('60')  # Minimum for 1 hour
            
            if balance.amount < min_required:
                return Response(
                    {"error": f"Insufficient balance. Minimum required: {min_required}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except:
            return Response(
                {"error": "User has no balance"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create a new booking record
        now = timezone.now()
        booking = Booking.objects.create(
            user=user,
            car=car,
            start_time=now,
            end_time=now + timezone.timedelta(days=1),  # Temporarily set for one day
            status='active',
            last_billing_time=now,
            minutes_billed=0,
            total_price=Decimal('0.00'),  # Initial amount
            pickup_location=f"{car.current_latitude},{car.current_longitude}" if car.current_latitude else ""
        )
        
        # Create a history record
        BookingHistory.objects.create(
            booking=booking,
            status='active',
            notes="Rental started"
        )
        
        # Update car status
        car.status = 'busy'
        car.save()
        
        return Response({
            "message": "Rental successfully started",
            "booking_id": booking.id
        })
    
    @action(detail=True, methods=['post'])
    def end_rental(self, request, pk=None):
        """End car rental"""
        booking = self.get_object()
        
        if booking.user != request.user and not request.user.is_staff:
            return Response(
                {"error": "You can only end your own rentals"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if booking.status != 'active':
            return Response(
                {"error": "Booking is not active"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # End the rental
        now = timezone.now()
        
        # Calculate the last billing
        time_diff = now - booking.last_billing_time
        minutes_to_bill = int(time_diff.total_seconds() / 60)
        
        if minutes_to_bill > 0:
            amount_to_bill = booking.car.price_per_minute * Decimal(str(minutes_to_bill))
            
            # Deduct money
            try:
                balance = booking.user.balance
                if balance.amount >= amount_to_bill:
                    balance.amount -= amount_to_bill
                    balance.save()
            except:
                pass  # If no balance, just end the rental
            
            booking.minutes_billed += minutes_to_bill
        
        # Update booking data
        booking.status = 'completed'
        booking.end_time = now
        booking.total_price = booking.car.price_per_minute * Decimal(str(booking.minutes_billed))
        booking.save()
        
        # Create a history record
        BookingHistory.objects.create(
            booking=booking,
            status='completed',
            notes=f"Rental ended. Total minutes: {booking.minutes_billed}, total price: {booking.total_price}"
        )
        
        # Update car status
        car = booking.car
        car.status = 'available'
        car.save()
        
        return Response({
            "message": "Rental successfully ended",
            "total_time": f"{booking.minutes_billed} minutes",
            "total_price": str(booking.total_price)
        })
