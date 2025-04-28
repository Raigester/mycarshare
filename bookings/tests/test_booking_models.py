# -*- coding: utf-8 -*-
from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from bookings.models import Booking, BookingHistory
from cars.models import Car, CarBrand, CarModel
from users.models import User


class BookingModelTest(TestCase):
    """Тести моделі Booking"""

    def setUp(self):
        """Налаштування тестового середовища"""
        self.user = User.objects.create_user(
            username="bookinguser",
            email="booking@example.com",
            password="testpassword123"
        )
        self.brand = CarBrand.objects.create(name="TestBrand")
        self.model = CarModel.objects.create(brand=self.brand, name="TestModel")
        self.car = Car.objects.create(
            model=self.model,
            year=2023,
            license_plate="AA1234BB",
            color="Чорний",
            mileage=10000,
            fuel_type="petrol",
            transmission="automatic",
            price_per_minute=Decimal("2.50"),
            seats=5,
            insurance_valid_until=timezone.now().date() + timedelta(days=365),
            technical_inspection_valid_until=timezone.now().date() + timedelta(days=365),
            main_photo="car_photos/test.jpg"
        )
        self.start_time = timezone.now() + timedelta(hours=1)
        self.end_time = self.start_time + timedelta(hours=2)

    def test_booking_creation(self):
        """Тест створення бронювання"""
        booking = Booking.objects.create(
            user=self.user,
            car=self.car,
            start_time=self.start_time,
            end_time=self.end_time,
            pickup_location="Test Pickup",
            return_location="Test Return",
            status="pending",
            total_price=Decimal("100.00")
        )
        self.assertEqual(booking.user, self.user)
        self.assertEqual(booking.car, self.car)
        self.assertEqual(booking.status, "pending")
        self.assertEqual(booking.total_price, Decimal("100.00"))

    def test_string_representation(self):
        """Тест рядкового представлення бронювання"""
        booking = Booking.objects.create(
            user=self.user,
            car=self.car,
            start_time=self.start_time,
            end_time=self.end_time,
            total_price=Decimal("100.00")
        )
        expected = f"Booking {booking.id} - {booking.car} ({booking.status})"
        self.assertEqual(str(booking), expected)

class BookingHistoryModelTest(TestCase):
    """Тести моделі BookingHistory"""

    def setUp(self):
        """Налаштування тестового середовища"""
        self.user = User.objects.create_user(
            username="historyuser",
            email="history@example.com",
            password="testpassword123"
        )
        self.brand = CarBrand.objects.create(name="HistoryBrand")
        self.model = CarModel.objects.create(brand=self.brand, name="HistoryModel")
        self.car = Car.objects.create(
            model=self.model,
            year=2023,
            license_plate="BB5678CC",
            color="Білий",
            mileage=5000,
            fuel_type="diesel",
            transmission="manual",
            price_per_minute=Decimal("3.00"),
            seats=4,
            insurance_valid_until=timezone.now().date() + timedelta(days=365),
            technical_inspection_valid_until=timezone.now().date() + timedelta(days=365),
            main_photo="car_photos/test2.jpg"
        )
        self.booking = Booking.objects.create(
            user=self.user,
            car=self.car,
            start_time=timezone.now() + timedelta(hours=1),
            end_time=timezone.now() + timedelta(hours=2),
            total_price=Decimal("50.00")
        )

    def test_booking_history_creation(self):
        """Тест створення запису історії бронювання"""
        history = BookingHistory.objects.create(
            booking=self.booking,
            status="pending",
            notes="Тестова примітка"
        )
        self.assertEqual(history.booking, self.booking)
        self.assertEqual(history.status, "pending")
        self.assertEqual(history.notes, "Тестова примітка")

    def test_booking_history_string_representation(self):
        """Тест рядкового представлення історії бронювання"""
        history = BookingHistory.objects.create(
            booking=self.booking,
            status="confirmed"
        )
        expected = f"History {self.booking.id} - {history.status} ({history.timestamp})"
        self.assertEqual(str(history), expected)
