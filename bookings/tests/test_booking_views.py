# -*- coding: utf-8 -*-
from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from bookings.models import Booking
from cars.models import Car, CarBrand, CarModel
from users.models import User, UserBalance


class BookingViewsTest(TestCase):
    """Тести представлень бронювань"""

    def setUp(self):
        """Налаштування тестового середовища"""
        self.user = User.objects.create_user(
            username="viewuser",
            email="view@example.com",
            password="testpassword123"
        )
        self.brand = CarBrand.objects.create(name="ViewBrand")
        self.model = CarModel.objects.create(brand=self.brand, name="ViewModel")
        self.car = Car.objects.create(
            model=self.model,
            year=2023,
            license_plate="EE1234FF",
            color="Червоний",
            mileage=12000,
            fuel_type="petrol",
            transmission="automatic",
            price_per_minute=Decimal("2.50"),
            seats=5,
            insurance_valid_until=timezone.now().date() + timedelta(days=365),
            technical_inspection_valid_until=timezone.now().date() + timedelta(days=365),
            main_photo="car_photos/test.jpg"
        )
        UserBalance.objects.create(user=self.user, amount=Decimal("500.00"))

        # Створюємо бронювання на майбутнє
        self.start_time = timezone.now() + timedelta(minutes=5)
        self.end_time = self.start_time + timedelta(hours=1)

        self.booking = Booking.objects.create(
            user=self.user,
            car=self.car,
            start_time=self.start_time,
            end_time=self.end_time,
            status="confirmed",
            total_price=Decimal("0.00"),
            minutes_billed=0,
            last_billing_time=timezone.now()
        )

    def test_active_bookings_view_authenticated(self):
        """Тест перегляду списку активних бронювань"""
        self.client.login(username="viewuser", password="testpassword123")
        url = reverse("booking-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "active_bookings.html")

    def test_completed_bookings_view_authenticated(self):
        """Тест перегляду списку завершених бронювань"""
        self.client.login(username="viewuser", password="testpassword123")
        url = reverse("completed-bookings")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "completed_bookings.html")

    def test_booking_detail_view_authenticated(self):
        """Тест перегляду деталей бронювання"""
        self.client.login(username="viewuser", password="testpassword123")
        url = reverse("booking-detail", args=[self.booking.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "booking_detail.html")

    def test_start_rental_get_view(self):
        """Тест відкриття сторінки початку оренди (GET)"""
        self.client.login(username="viewuser", password="testpassword123")
        url = reverse("start-rental")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "start_rental.html")

    def test_end_rental_get_view(self):
        """Тест відкриття сторінки завершення оренди (GET)"""
        self.booking.start_time = timezone.now() - timedelta(hours=1)
        self.booking.end_time = None
        self.booking.status = "active"
        self.booking.save()

        self.client.login(username="viewuser", password="testpassword123")
        url = reverse("end-rental", args=[self.booking.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "end_rental.html")

    def test_end_rental_post_complete_rental(self):
        """Тест успішного завершення оренди (POST)"""
        self.booking.start_time = timezone.now() - timedelta(hours=1)
        self.booking.end_time = None
        self.booking.status = "active"
        self.booking.save()

        self.client.login(username="viewuser", password="testpassword123")
        url = reverse("end-rental", args=[self.booking.id])
        form_data = {
            "confirm_end": True
        }
        response = self.client.post(url, form_data)
        self.booking.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.booking.status, "completed")

class BookingPermissionsTest(TestCase):
    """Тести прав доступу до бронювань"""

    def setUp(self):
        """Налаштування тестового середовища"""
        self.user1 = User.objects.create_user(
            username="user1",
            email="user1@example.com",
            password="testpassword123"
        )
        self.user2 = User.objects.create_user(
            username="user2",
            email="user2@example.com",
            password="testpassword123"
        )
        self.brand = CarBrand.objects.create(name="PermBrand")
        self.model = CarModel.objects.create(brand=self.brand, name="PermModel")
        self.car = Car.objects.create(
            model=self.model,
            year=2023,
            license_plate="GG1234HH",
            color="Синій",
            mileage=8000,
            fuel_type="diesel",
            transmission="manual",
            price_per_minute=Decimal("2.00"),
            seats=4,
            insurance_valid_until=timezone.now().date() + timedelta(days=365),
            technical_inspection_valid_until=timezone.now().date() + timedelta(days=365),
            main_photo="car_photos/test2.jpg"
        )

        self.start_time = timezone.now() + timedelta(minutes=5)
        self.end_time = self.start_time + timedelta(hours=1)

        self.booking = Booking.objects.create(
            user=self.user1,
            car=self.car,
            start_time=self.start_time,
            end_time=self.end_time,
            status="confirmed",
            total_price=Decimal("0.00"),
            last_billing_time=timezone.now()
        )

    def test_forbidden_booking_detail_for_other_user(self):
        """Тест заборони перегляду бронювання іншого користувача"""
        self.client.login(username="user2", password="testpassword123")
        url = reverse("booking-detail", args=[self.booking.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_forbidden_end_rental_for_other_user(self):
        """Тест заборони завершення оренди іншого користувача"""
        self.client.login(username="user2", password="testpassword123")
        url = reverse("end-rental", args=[self.booking.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
