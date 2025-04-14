from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import timedelta
from .models import Payment, Invoice
from .serializers import PaymentSerializer, InvoiceSerializer, PaymentCreateSerializer
from bookings.models import Booking

class PaymentPermission(permissions.BasePermission):
    """Custom permissions for payments"""
    
    def has_object_permission(self, request, view, obj):
        # Admins have full access
        if request.user.is_staff:
            return True
        
        # Users have access only to their own payments
        return obj.user == request.user

class InvoicePermission(permissions.BasePermission):
    """Custom permissions for invoices"""
    
    def has_object_permission(self, request, view, obj):
        # Admins have full access
        if request.user.is_staff:
            return True
        
        # Users have access only to their own invoices
        return obj.user == request.user

class PaymentViewSet(viewsets.ModelViewSet):
    """API for payments"""
    
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated, PaymentPermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'payment_type', 'booking']
    ordering_fields = ['created_at', 'amount']
    
    def get_queryset(self):
        # Admins see all payments, users see only their own
        user = self.request.user
        if not user.is_authenticated:
            return Payment.objects.none()
        if user.is_staff:
            return Payment.objects.all()
        return Payment.objects.filter(user=user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PaymentCreateSerializer
        return PaymentSerializer
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def complete_payment(self, request, pk=None):
        """Complete a payment (admin only)"""
        payment = self.get_object()
        
        # Check that the payment is pending
        if payment.status != 'pending':
            return Response(
                {"error": "Only payments with 'Pending' status can be completed"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update the payment
        payment.status = 'completed'
        payment.transaction_id = request.data.get('transaction_id', f'admin-{timezone.now().timestamp()}')
        payment.save()
        
        # If there is an associated invoice, update its status
        invoice = Invoice.objects.filter(payment=payment).first()
        if invoice:
            invoice.status = 'paid'
            invoice.save()
        
        # If the payment is associated with a booking, update its status
        booking = payment.booking
        if booking and booking.status == 'pending' and payment.payment_type == 'booking':
            booking.status = 'confirmed'
            booking.save()
            
            # Create a booking history record
            from bookings.models import BookingHistory
            BookingHistory.objects.create(
                booking=booking,
                status='confirmed',
                notes=f"Booking confirmed after payment (payment ID: {payment.id})"
            )
        
        return Response({"message": "Payment successfully completed"})
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def refund_payment(self, request, pk=None):
        """Refund a payment (admin only)"""
        payment = self.get_object()
        
        # Check if a refund is possible
        if payment.status != 'completed':
            return Response(
                {"error": "Only completed payments can be refunded"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create a new payment (refund)
        refund = Payment.objects.create(
            user=payment.user,
            booking=payment.booking,
            amount=payment.amount,
            payment_type='refund',
            status='completed',
            payment_method=payment.payment_method,
            transaction_id=f"refund-{payment.transaction_id}",
            description=f"Refund for payment {payment.id}: {request.data.get('reason', 'No reason provided')}"
        )
        
        # Update the original payment
        payment.status = 'refunded'
        payment.save()
        
        return Response({
            "message": "Funds successfully refunded",
            "refund_id": refund.id
        })

class InvoiceViewSet(viewsets.ModelViewSet):
    """API for invoices"""
    
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated, InvoicePermission]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'booking']
    ordering_fields = ['created_at', 'due_date', 'amount']
    
    def get_queryset(self):
        # Admins see all invoices, users see only their own
        user = self.request.user
        if not user.is_authenticated:
            return Invoice.objects.none()
        if user.is_staff:
            return Invoice.objects.all()
        return Invoice.objects.filter(user=user)
    
    @action(detail=True, methods=['post'])
    def pay(self, request, pk=None):
        """Pay an invoice"""
        invoice = self.get_object()
        
        # Check if payment is possible
        if invoice.status != 'pending':
            return Response(
                {"error": "Only invoices with 'Pending' status can be paid"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if invoice.due_date < timezone.now():
            return Response(
                {"error": "The invoice payment deadline has passed"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create a payment (here would be integration with a payment system)
        payment_method = request.data.get('payment_method', 'card')
        payment = Payment.objects.create(
            user=invoice.user,
            booking=invoice.booking,
            amount=invoice.amount,
            payment_type='booking' if invoice.booking else 'other',
            status='pending',  # Initially pending, will be updated later
            payment_method=payment_method,
            description=f"Payment for invoice {invoice.id}: {invoice.description}"
        )
        
        # Link the payment to the invoice
        invoice.payment = payment
        invoice.save()
        
        # In a real system, this would redirect to a payment gateway
        return Response({
            "message": "Payment created, redirect the user to the payment gateway",
            "payment_id": payment.id,
            "amount": float(payment.amount),
            "payment_method": payment_method
        })
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def cancel(self, request, pk=None):
        """Cancel an invoice (admin only)"""
        invoice = self.get_object()
        
        # Check if cancellation is possible
        if invoice.status != 'pending':
            return Response(
                {"error": "Only invoices with 'Pending' status can be canceled"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Cancel the invoice
        invoice.status = 'cancelled'
        invoice.save()
        
        return Response({"message": "Invoice successfully canceled"})
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get overdue invoices"""
        now = timezone.now()
        
        if request.user.is_staff:
            invoices = Invoice.objects.filter(
                status='pending',
                due_date__lt=now
            ).order_by('due_date')
        else:
            invoices = Invoice.objects.filter(
                user=request.user,
                status='pending',
                due_date__lt=now
            ).order_by('due_date')
        
        serializer = self.get_serializer(invoices, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def create_booking_invoice(self, request):
        """Create an invoice for a booking (admin only)"""
        booking_id = request.data.get('booking_id')
        
        try:
            booking = Booking.objects.get(id=booking_id)
        except Booking.DoesNotExist:
            return Response(
                {"error": "Booking not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if there is already an invoice for this booking
        existing_invoice = Invoice.objects.filter(
            booking=booking,
            status='pending'
        ).first()
        
        if existing_invoice:
            return Response(
                {"error": "There is already an unpaid invoice for this booking"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create an invoice with a due date 24 hours from now
        due_date = timezone.now() + timedelta(hours=24)
        invoice = Invoice.objects.create(
            user=booking.user,
            booking=booking,
            amount=booking.total_price,
            description=f"Payment for car booking {booking.car.model} from {booking.start_time} to {booking.end_time}",
            due_date=due_date
        )
        
        serializer = self.get_serializer(invoice)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
