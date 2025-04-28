# -*- coding: utf-8 -*-
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from payments.models import LiqPayPayment, Payment, PaymentTransaction


User = get_user_model()

class PaymentModelTest(TestCase):
    """Тести моделі Payment"""

    def setUp(self):
        """Налаштування тестового середовища"""
        self.test_user = User.objects.create_user(
            username="paymentuser",
            email="payment@example.com",
            password="testpassword123"
        )
        self.payment = Payment.objects.create(
            user=self.test_user,
            amount=Decimal("100.00"),
            payment_provider="liqpay",
            status="pending"
        )

    def test_payment_creation(self):
        """Тест створення платежу"""
        self.assertEqual(self.payment.user, self.test_user)
        self.assertEqual(self.payment.amount, Decimal("100.00"))
        self.assertEqual(self.payment.payment_provider, "liqpay")
        self.assertEqual(self.payment.status, "pending")

    def test_payment_string_representation(self):
        """Тест рядкового представлення платежу"""
        expected_str = (
            f"{self.test_user.username} - {self.payment.amount:.2f} - "
            f"{self.payment.payment_provider} - {self.payment.status}"
        )
        self.assertEqual(str(self.payment), expected_str)

class LiqPayPaymentModelTest(TestCase):
    """Тести моделі LiqPayPayment"""

    def setUp(self):
        """Налаштування тестового середовища"""
        self.test_user = User.objects.create_user(
            username="liqpayuser",
            email="liqpay@example.com",
            password="testpassword123"
        )
        self.payment = Payment.objects.create(
            user=self.test_user,
            amount=Decimal("200.00"),
            payment_provider="liqpay",
            status="completed"
        )
        self.liqpay_payment = LiqPayPayment.objects.create(
            payment=self.payment,
            liqpay_order_id="ORDER123456"
        )

    def test_liqpay_payment_creation(self):
        """Тест створення LiqPay-платежу"""
        self.assertEqual(self.liqpay_payment.payment, self.payment)
        self.assertEqual(self.liqpay_payment.liqpay_order_id, "ORDER123456")

    def test_liqpay_payment_string_representation(self):
        """Тест рядкового представлення LiqPay-платежу"""
        expected_str = "LiqPay payment: ORDER123456"
        self.assertEqual(str(self.liqpay_payment), expected_str)

class PaymentTransactionModelTest(TestCase):
    """Тести моделі PaymentTransaction"""

    def setUp(self):
        """Налаштування тестового середовища"""
        self.test_user = User.objects.create_user(
            username="transactionuser",
            email="transaction@example.com",
            password="testpassword123"
        )
        self.transaction = PaymentTransaction.objects.create(
            user=self.test_user,
            amount=Decimal("50.00"),
            transaction_type="deposit",
            balance_after=Decimal("150.00")
        )

    def test_transaction_creation(self):
        """Тест створення транзакції"""
        self.assertEqual(self.transaction.user, self.test_user)
        self.assertEqual(self.transaction.amount, Decimal("50.00"))
        self.assertEqual(self.transaction.transaction_type, "deposit")
        self.assertEqual(self.transaction.balance_after, Decimal("150.00"))

    def test_transaction_string_representation(self):
        """Тест рядкового представлення транзакції"""
        expected_str = (
            f"{self.test_user.username} - {self.transaction.transaction_type} - "
            f"{self.transaction.amount:.2f}"
        )
        self.assertEqual(str(self.transaction), expected_str)
