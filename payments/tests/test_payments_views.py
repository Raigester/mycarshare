# -*- coding: utf-8 -*-
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from payments.models import Payment, PaymentTransaction


User = get_user_model()

class PaymentViewsTest(TestCase):
    """Тести представлень платежів"""

    def setUp(self):
        """Налаштування тестового середовища"""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword123"
        )
        self.payment = Payment.objects.create(
            user=self.user,
            amount=Decimal("100.00"),
            payment_provider="liqpay",
            status="pending"
        )

    def test_payment_list_view_authenticated(self):
        """Тест доступу до списку платежів для автентифікованого користувача"""
        self.client.login(username="testuser", password="testpassword123")
        url = reverse("payment-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "payment_list.html")

    def test_payment_detail_view_authenticated(self):
        """Тест перегляду деталей платежу для автентифікованого користувача"""
        self.client.login(username="testuser", password="testpassword123")
        url = reverse("payment-detail", args=[self.payment.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "payment_detail.html")

    def test_create_payment_view_get(self):
        """Тест відкриття форми створення платежу"""
        self.client.login(username="testuser", password="testpassword123")
        url = reverse("create-payment")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "create_payment.html")

    def test_payment_success_view(self):
        """Тест обробки успішного платежу"""
        self.client.login(username="testuser", password="testpassword123")
        url = reverse("payment-success")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("payment-list"))

    def test_payment_cancel_view(self):
        """Тест обробки скасування платежу"""
        self.client.login(username="testuser", password="testpassword123")
        url = reverse("payment-cancel")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("payment-list"))

    def test_process_payment_view_without_session(self):
        """Тест обробки платежу без даних у сесії"""
        self.client.login(username="testuser", password="testpassword123")
        url = reverse("payment-process")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("create-payment"))

class TransactionViewsTest(TestCase):
    """Тести представлень транзакцій"""

    def setUp(self):
        """Налаштування тестового середовища"""
        self.user = User.objects.create_user(
            username="transactionuser",
            email="transaction@example.com",
            password="testpassword123"
        )
        self.transaction = PaymentTransaction.objects.create(
            user=self.user,
            amount=Decimal("50.00"),
            transaction_type="deposit",
            balance_after=Decimal("150.00")
        )

    def test_transaction_list_view_authenticated(self):
        """Тест доступу до списку транзакцій для автентифікованого користувача"""
        self.client.login(username="transactionuser", password="testpassword123")
        url = reverse("transaction-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "transaction_list.html")
