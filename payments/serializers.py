from rest_framework import serializers
from .models import Payment, LiqPayPayment, PaymentTransaction, WayForPayPayment
from django.conf import settings
from decimal import Decimal

class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for the Payment model"""
    
    class Meta:
        model = Payment
        fields = ('id', 'user', 'amount', 'payment_provider', 'status', 'created_at')
        read_only_fields = ('user', 'status', 'created_at')

class WayForPayPaymentSerializer(serializers.ModelSerializer):
    """Serializer for WayForPay payments"""
    
    class Meta:
        model = WayForPayPayment
        fields = ('payment', 'wayforpay_order_id', 'wayforpay_transaction_id', 'wayforpay_signature', 'wayforpay_status')
        read_only_fields = ('wayforpay_order_id', 'wayforpay_transaction_id', 'wayforpay_signature', 'wayforpay_status')

class LiqPayPaymentSerializer(serializers.ModelSerializer):
    """Serializer for LiqPay payments"""
    
    class Meta:
        model = LiqPayPayment  
        fields = ('payment', 'liqpay_order_id', 'liqpay_signature', 'liqpay_data')
        read_only_fields = ('liqpay_order_id', 'liqpay_signature', 'liqpay_data')

class PaymentTransactionSerializer(serializers.ModelSerializer):
    """Serializer for payment transactions"""
    
    class Meta:
        model = PaymentTransaction
        fields = ('id', 'user', 'payment', 'amount', 'transaction_type', 
                  'description', 'balance_after', 'created_at')
        read_only_fields = ('user', 'payment', 'balance_after', 'created_at')

class CreatePaymentSerializer(serializers.Serializer):
    """Serializer for creating a payment"""
    
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    payment_provider = serializers.ChoiceField(choices=Payment.PAYMENT_PROVIDER_CHOICES)
    
    def validate_amount(self, value):
        """Validate payment amount"""
        min_payment = Decimal(settings.MIN_PAYMENT_AMOUNT)
        max_payment = Decimal(settings.MAX_PAYMENT_AMOUNT)
        
        if value < min_payment:
            raise serializers.ValidationError(
                f"Amount must be at least {min_payment}"
            )
        
        if value > max_payment:
            raise serializers.ValidationError(
                f"Amount cannot exceed {max_payment}"
            )
        
        return value
