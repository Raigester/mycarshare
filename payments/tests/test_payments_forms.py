# -*- coding: utf-8 -*-
from decimal import Decimal

from django.conf import settings
from django.test import TestCase

from payments.forms import CreatePaymentForm, PaymentFilterForm, TransactionFilterForm


class CreatePaymentFormTest(TestCase):
    """Тести форми CreatePaymentForm"""

    def test_form_valid_data(self):
        """Тест валідних даних форми"""
        form_data = {
            "amount": Decimal(settings.MIN_PAYMENT_AMOUNT) + Decimal("10.00"),
            "payment_provider": "liqpay",
        }
        form = CreatePaymentForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_invalid_low_amount(self):
        """Тест помилки при занадто малій сумі"""
        form_data = {
            "amount": Decimal(settings.MIN_PAYMENT_AMOUNT) - Decimal("1.00"),
            "payment_provider": "liqpay",
        }
        form = CreatePaymentForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("amount", form.errors)

    def test_form_invalid_high_amount(self):
        """Тест помилки при занадто великій сумі"""
        form_data = {
            "amount": Decimal(settings.MAX_PAYMENT_AMOUNT) + Decimal("1.00"),
            "payment_provider": "liqpay",
        }
        form = CreatePaymentForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("amount", form.errors)

class PaymentFilterFormTest(TestCase):
    """Тести форми PaymentFilterForm"""

    def test_form_empty_data(self):
        """Тест форми без даних"""
        form = PaymentFilterForm(data={})
        self.assertTrue(form.is_valid())

    def test_form_with_valid_filters(self):
        """Тест форми з валідними фільтрами"""
        form_data = {
            "status": "completed",
            "payment_provider": "liqpay",
            "date_from": "2024-01-01",
            "date_to": "2024-12-31"
        }
        form = PaymentFilterForm(data=form_data)
        self.assertTrue(form.is_valid())

class TransactionFilterFormTest(TestCase):
    """Тести форми TransactionFilterForm"""

    def test_form_empty_data(self):
        """Тест форми без даних"""
        form = TransactionFilterForm(data={})
        self.assertTrue(form.is_valid())

    def test_form_with_valid_filters(self):
        """Тест форми з валідними фільтрами"""
        form_data = {
            "transaction_type": "deposit",
            "date_from": "2024-01-01",
            "date_to": "2024-12-31"
        }
        form = TransactionFilterForm(data=form_data)
        self.assertTrue(form.is_valid())
