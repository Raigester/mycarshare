from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _


User = get_user_model()

class Payment(models.Model):
    """Базова модель платежу"""
    PAYMENT_STATUS_CHOICES = (
        ("pending", _("Очікується")),
        ("completed", _("Завершено")),
        ("failed", _("Помилка")),
        ("cancelled", _("Скасовано")),
    )

    PAYMENT_PROVIDER_CHOICES = (
        ("liqpay", _("LiqPay")),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payments")  # Зв'язок з користувачем
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Сума платежу
    payment_provider = models.CharField(max_length=20, choices=PAYMENT_PROVIDER_CHOICES)  # Провайдер платежу
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default="pending")  # Статус платежу
    created_at = models.DateTimeField(auto_now_add=True)  # Дата створення платежу
    updated_at = models.DateTimeField(auto_now=True)  # Дата останнього оновлення платежу

    def __str__(self):
        return f"{self.user.username} - {self.amount} - {self.payment_provider} - {self.status}"

class LiqPayPayment(models.Model):
    """Деталі платежу через LiqPay"""
    payment = models.OneToOneField(
        Payment,
        on_delete=models.CASCADE,
        related_name="liqpay_details"
    )  # Зв'язок до моделі Payment
    liqpay_order_id = models.CharField(max_length=255)  # Ідентифікатор замовлення LiqPay
    liqpay_signature = models.TextField(blank=True, null=True)  # Підпис LiqPay
    liqpay_data = models.TextField(blank=True, null=True)  # Дані LiqPay

    def __str__(self):
        return f"LiqPay payment: {self.liqpay_order_id}"

class PaymentTransaction(models.Model):
    """Модель для зберігання історії транзакцій"""
    TRANSACTION_TYPE_CHOICES = (
        ("deposit", _("Поповнення")),
        ("withdrawal", _("Виведення")),
        ("booking", _("Плата за бронювання")),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transactions")  # Зв'язок з користувачем
    payment = models.ForeignKey(
        Payment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions"
    )  # Пов'язаний платіж
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Сума транзакції
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)  # Тип транзакції
    description = models.TextField(blank=True)  # Опис транзакції
    balance_after = models.DecimalField(max_digits=10, decimal_places=2)  # Баланс після транзакції
    created_at = models.DateTimeField(auto_now_add=True)  # Дата створення транзакції

    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} - {self.amount}"
