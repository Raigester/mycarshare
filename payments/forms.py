from decimal import Decimal

from django import forms
from django.conf import settings

from .models import Payment, PaymentTransaction


class CreatePaymentForm(forms.Form):
    """Форма для створення нового платежу"""

    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal(settings.MIN_PAYMENT_AMOUNT),
        max_value=Decimal(settings.MAX_PAYMENT_AMOUNT),
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "step": "0.01",
            "placeholder": "0.00"
        })
    )

    payment_provider = forms.ChoiceField(
        choices=Payment.PAYMENT_PROVIDER_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["amount"].help_text = (
            f"Мінімальна сума: {settings.MIN_PAYMENT_AMOUNT}, "
            f"Максимальна сума: {settings.MAX_PAYMENT_AMOUNT}"
        )

    def clean_amount(self):
        """Валідація суми платежу"""
        amount = self.cleaned_data.get("amount")
        min_payment = Decimal(settings.MIN_PAYMENT_AMOUNT)
        max_payment = Decimal(settings.MAX_PAYMENT_AMOUNT)

        if amount < min_payment:
            raise forms.ValidationError(
                f"Сума повинна бути не меншою за {min_payment}"
            )

        if amount > max_payment:
            raise forms.ValidationError(
                f"Сума не може перевищувати {max_payment}"
            )

        return amount

class PaymentFilterForm(forms.Form):
    """Форма для фільтрації платежів"""

    STATUS_CHOICES = (
        ("", "Усі статуси"),
    ) + Payment.PAYMENT_STATUS_CHOICES

    PROVIDER_CHOICES = (
        ("", "Усі провайдери"),
    ) + Payment.PAYMENT_PROVIDER_CHOICES

    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-select"})
    )

    payment_provider = forms.ChoiceField(
        choices=PROVIDER_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-select"})
    )

    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"})
    )

    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"})
    )

class TransactionFilterForm(forms.Form):
    """Форма для фільтрації транзакцій"""

    TYPE_CHOICES = (
        ("", "Усі типи"),
    ) + PaymentTransaction.TRANSACTION_TYPE_CHOICES

    transaction_type = forms.ChoiceField(
        choices=TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-select"})
    )

    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"})
    )

    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"})
    )
