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
