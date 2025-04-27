from rest_framework import serializers
from .models import Payment, LiqPayPayment, PaymentTransaction
from django.conf import settings
from decimal import Decimal

class PaymentSerializer(serializers.ModelSerializer):
    """Серіалізатор для моделі Payment"""
    
    class Meta:
        model = Payment
        fields = ('id', 'user', 'amount', 'payment_provider', 'status', 'created_at')
        read_only_fields = ('user', 'status', 'created_at')

class LiqPayPaymentSerializer(serializers.ModelSerializer):
    """Серіалізатор для платежів через LiqPay"""
    
    class Meta:
        model = LiqPayPayment  
        fields = ('payment', 'liqpay_order_id', 'liqpay_signature', 'liqpay_data')
        read_only_fields = ('liqpay_order_id', 'liqpay_signature', 'liqpay_data')

class PaymentTransactionSerializer(serializers.ModelSerializer):
    """Серіалізатор для транзакцій платежів"""
    
    class Meta:
        model = PaymentTransaction
        fields = ('id', 'user', 'payment', 'amount', 'transaction_type', 
                  'description', 'balance_after', 'created_at')
        read_only_fields = ('user', 'payment', 'balance_after', 'created_at')

class CreatePaymentSerializer(serializers.Serializer):
    """Серіалізатор для створення платежу"""
    
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    payment_provider = serializers.ChoiceField(choices=Payment.PAYMENT_PROVIDER_CHOICES)
    
    def validate_amount(self, value):
        """Валідація суми платежу"""
        min_payment = Decimal(settings.MIN_PAYMENT_AMOUNT)
        max_payment = Decimal(settings.MAX_PAYMENT_AMOUNT)
        
        if value < min_payment:
            raise serializers.ValidationError(
                f"Сума має бути не меншою за {min_payment}"
            )
        
        if value > max_payment:
            raise serializers.ValidationError(
                f"Сума не може перевищувати {max_payment}"
            )
        
        return value
