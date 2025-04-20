from django.contrib import admin
from .models import Payment, LiqPayPayment, PaymentTransaction, WayForPayPayment

class WayForPayPaymentInline(admin.StackedInline):
    model = WayForPayPayment
    extra = 0

class LiqPayPaymentInline(admin.StackedInline):
    model = LiqPayPayment
    extra = 0

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'amount', 'payment_provider', 'status', 'created_at')
    list_filter = ('payment_provider', 'status', 'created_at')
    search_fields = ('user__username', 'user__email', 'provider_payment_id')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [WayForPayPaymentInline, LiqPayPaymentInline]

@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'amount', 'transaction_type', 'balance_after', 'created_at')
    list_filter = ('transaction_type', 'created_at')
    search_fields = ('user__username', 'user__email', 'description')
    readonly_fields = ('user', 'payment', 'amount', 'transaction_type', 'balance_after', 'created_at')
