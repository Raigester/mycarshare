# -*- coding: utf-8 -*-
from datetime import date, timedelta
from decimal import Decimal

from django.test import TestCase

from cars.models import Car, CarBrand, CarModel, CarPhoto, CarReview
from users.models import User


class CarBrandModelTest(TestCase):
    """Тести моделі CarBrand"""

    def test_car_brand_creation(self):
        """Тест створення бренду автомобіля"""
        brand = CarBrand.objects.create(name="TestBrand")
        self.assertEqual(str(brand), "TestBrand")

class CarModelModelTest(TestCase):
    """Тести моделі CarModel"""

    def setUp(self):
        """Налаштування тестового середовища"""
        self.brand = CarBrand.objects.create(name="TestBrand")

    def test_car_model_creation(self):
        """Тест створення моделі автомобіля"""
        model = CarModel.objects.create(brand=self.brand, name="TestModel")
        self.assertEqual(str(model), "TestBrand TestModel")

class CarModelTest(TestCase):
    """Тести моделі Car"""

    def setUp(self):
        """Налаштування тестового середовища"""
        self.brand = CarBrand.objects.create(name="TestBrand")
        self.model = CarModel.objects.create(brand=self.brand, name="TestModel")

    def test_car_creation(self):
        """Тест створення автомобіля"""
        car = Car.objects.create(
            model=self.model,
            year=2023,
            license_plate="AA1234BB",
            color="Чорний",
            mileage=10000,
            fuel_type="petrol",
            transmission="manual",
            price_per_minute=Decimal("2.50"),
            engine_capacity=Decimal("1.6"),
            power=120,
            seats=5,
            has_air_conditioning=True,
            has_gps=True,
            has_child_seat=False,
            has_bluetooth=True,
            has_usb=True,
            status="available",
            current_latitude="50.4501",
            current_longitude="30.5234",
            main_photo="car_photos/test.jpg",
            insurance_valid_until=date.today() + timedelta(days=365),
            technical_inspection_valid_until=date.today() + timedelta(days=365)
        )
        expected_str = f"{self.model} ({car.license_plate})"
        self.assertEqual(str(car), expected_str)

class CarPhotoModelTest(TestCase):
    """Тести моделі CarPhoto"""

    def setUp(self):
        """Налаштування тестового середовища"""
        self.brand = CarBrand.objects.create(name="PhotoBrand")
        self.model = CarModel.objects.create(brand=self.brand, name="PhotoModel")
        self.car = Car.objects.create(
            model=self.model,
            year=2022,
            license_plate="CC1234DD",
            color="Білий",
            mileage=5000,
            fuel_type="diesel",
            transmission="automatic",
            price_per_minute=Decimal("3.00"),
            seats=5,
            insurance_valid_until=date.today() + timedelta(days=365),
            technical_inspection_valid_until=date.today() + timedelta(days=365),
            main_photo="car_photos/test2.jpg"
        )

    def test_car_photo_creation(self):
        """Тест створення фото автомобіля"""
        photo = CarPhoto.objects.create(
            car=self.car,
            photo="car_photos/test_photo.jpg",
            caption="Тестове фото"
        )
        self.assertIn(str(self.car), str(photo))

class CarReviewModelTest(TestCase):
    """Тести моделі CarReview"""

    def setUp(self):
        """Налаштування тестового середовища"""
        self.user = User.objects.create_user(
            username="reviewuser",
            email="review@example.com",
            password="testpassword123"
        )
        self.brand = CarBrand.objects.create(name="ReviewBrand")
        self.model = CarModel.objects.create(brand=self.brand, name="ReviewModel")
        self.car = Car.objects.create(
            model=self.model,
            year=2024,
            license_plate="DD1234EE",
            color="Сірий",
            mileage=8000,
            fuel_type="electric",
            transmission="automatic",
            price_per_minute=Decimal("4.00"),
            seats=5,
            insurance_valid_until=date.today() + timedelta(days=365),
            technical_inspection_valid_until=date.today() + timedelta(days=365),
            main_photo="car_photos/test3.jpg"
        )

    def test_car_review_creation(self):
        """Тест створення відгуку на автомобіль"""
        review = CarReview.objects.create(
            car=self.car,
            user=self.user,
            rating=5,
            comment="Чудова машина!"
        )
        expected_str = f"Відгук від {self.user.username} для {self.car}"
        self.assertEqual(str(review), expected_str)
