from django.contrib import admin
from .models import Payment, LiqPayPayment, PaymentTransaction

class LiqPayPaymentInline(admin.StackedInline):
    """Вбудована модель для відображення деталей платежів через LiqPay"""
    model = LiqPayPayment
    extra = 0  # Не додавати порожні рядки для нових записів

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Адмін-панель для платежів"""
    list_display = ('id', 'user', 'amount', 'payment_provider', 'status', 'created_at')  # Поля для відображення у списку
    list_filter = ('payment_provider', 'status', 'created_at')  # Фільтри для списку
    search_fields = ('user__username', 'user__email')  # Поля для пошуку
    readonly_fields = ('created_at', 'updated_at')  # Поля лише для читання
    inlines = [LiqPayPaymentInline]  # Вбудована модель для деталей LiqPay

@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    """Адмін-панель для транзакцій платежів"""
    list_display = ('id', 'user', 'amount', 'transaction_type', 'balance_after', 'created_at')  # Поля для відображення у списку
    list_filter = ('transaction_type', 'created_at')  # Фільтри для списку
    search_fields = ('user__username', 'user__email', 'description')  # Поля для пошуку
    readonly_fields = ('user', 'payment', 'amount', 'transaction_type', 'balance_after', 'created_at')  # Поля лише для читання
