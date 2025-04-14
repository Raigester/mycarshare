from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator

class Payment(models.Model):
    """Model for payments"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded')
    ]
    
    PAYMENT_TYPES = [
        ('booking', 'Booking payment'),
        ('deposit', 'Deposit'),
        ('fine', 'Fine'),
        ('refund', 'Refund')
    ]
    
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='payments')
    booking = models.ForeignKey('bookings.Booking', on_delete=models.CASCADE, 
                                related_name='payments', null=True, blank=True)
    
    amount = models.DecimalField(max_digits=10, decimal_places=2, 
                          validators=[MinValueValidator(Decimal('0.01'))])
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Payment information
    transaction_id = models.CharField(max_length=100, blank=True)
    payment_method = models.CharField(max_length=50, blank=True)
    
    # Additional information
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Payment {self.id} - {self.user.username} ({self.amount} RUB)"

class Invoice(models.Model):
    """Model for invoices"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending payment'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired')
    ]
    
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='invoices')
    booking = models.ForeignKey('bookings.Booking', on_delete=models.CASCADE, 
                                related_name='invoices', null=True, blank=True)
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Payment deadline
    due_date = models.DateTimeField()
    
    # Service information
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    payment = models.OneToOneField(Payment, on_delete=models.SET_NULL, 
                                   null=True, blank=True, related_name='invoice')
    
    def __str__(self):
        return f"Invoice {self.id} - {self.user.username} ({self.amount} RUB)"
