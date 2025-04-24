from decimal import Decimal
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class Payment(models.Model):
    """Base payment model"""
    PAYMENT_STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
        ('cancelled', _('Cancelled')),
        ('refunded', _('Refunded')),
    )
    
    PAYMENT_PROVIDER_CHOICES = (
        ('liqpay', _('LiqPay')),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_provider = models.CharField(max_length=20, choices=PAYMENT_PROVIDER_CHOICES)
    provider_payment_id = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.amount} - {self.payment_provider} - {self.status}"

class LiqPayPayment(models.Model):
    """LiqPay payment details"""
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='liqpay_details')
    liqpay_order_id = models.CharField(max_length=255)
    liqpay_signature = models.TextField(blank=True, null=True)
    liqpay_data = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"LiqPay payment: {self.liqpay_order_id}"

class PaymentTransaction(models.Model):
    """Model to store transaction history"""
    TRANSACTION_TYPE_CHOICES = (
        ('deposit', _('Deposit')),
        ('withdrawal', _('Withdrawal')),
        ('refund', _('Refund')),
        ('booking', _('Booking Fee')),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    description = models.TextField(blank=True)
    balance_after = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} - {self.amount}"
