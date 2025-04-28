# -*- coding: utf-8 -*-
from decimal import Decimal

from django.test import TestCase

from bookings.forms import BookingEndRentalForm, BookingStartRentalForm
from cars.models import Car, CarBrand, CarModel
from users.models import User, UserBalance


class BookingStartRentalFormTest(TestCase):
    """Тести форми BookingStartRentalForm"""

    def setUp(self):
        """Налаштування тестового середовища"""
        self.user = User.objects.create_user(
            username="formuser",
            email="form@example.com",
            password="testpassword123"
        )
        self.brand = CarBrand.objects.create(name="FormBrand")
        self.model = CarModel.objects.create(brand=self.brand, name="FormModel")
        self.car = Car.objects.create(
            model=self.model,
            year=2022,
            license_plate="CC1234DD",
            color="Сірий",
            mileage=15000,
            fuel_type="petrol",
            transmission="automatic",
            price_per_minute=Decimal("3.00"),
            seats=5,
            insurance_valid_until="2030-01-01",
            technical_inspection_valid_until="2030-01-01",
            main_photo="car_photos/test3.jpg"
        )
        UserBalance.objects.create(user=self.user, amount=Decimal("500.00"))

    def test_valid_start_rental_form(self):
        """Тест валідної форми початку оренди"""
        form_data = {
            "car": self.car.id,
            "confirm_start": True
        }
        form = BookingStartRentalForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid())

    def test_invalid_start_rental_due_to_low_balance(self):
        """Тест невалідної форми через недостатній баланс"""
        balance = UserBalance.objects.get(user=self.user)
        balance.amount = Decimal("10.00")
        balance.save()
        self.user.refresh_from_db()

        form_data = {
            "car": self.car.id,
            "confirm_start": True
        }
        form = BookingStartRentalForm(data=form_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)

class BookingEndRentalFormTest(TestCase):
    """Тести форми BookingEndRentalForm"""

    def test_valid_end_rental_form(self):
        """Тест валідної форми завершення оренди"""
        form_data = {
            "confirm_end": True
        }
        form = BookingEndRentalForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_end_rental_form_without_confirmation(self):
        """Тест невалідної форми без підтвердження завершення"""
        form_data = {}
        form = BookingEndRentalForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("confirm_end", form.errors)
