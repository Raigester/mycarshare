# -*- coding: utf-8 -*-
import tempfile
from datetime import date, timedelta
from decimal import Decimal
from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from PIL import Image

from cars.forms import (
    CarBrandForm,
    CarFilterForm,
    CarForm,
    CarLocationForm,
    CarModelForm,
    CarPhotoForm,
    CarReviewForm,
    CarStatusForm,
)
from cars.models import Car, CarBrand, CarModel
from users.models import User


TEMP_MEDIA_ROOT = tempfile.mkdtemp()

def get_test_image(name="test_image.jpg"):
    """Генерація тестового зображення."""
    image = Image.new("RGB", (100, 100), color="red")
    temp_file = BytesIO()
    image.save(temp_file, format="JPEG")
    temp_file.seek(0)
    return SimpleUploadedFile(name, temp_file.read(), content_type="image/jpeg")

@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class CarBrandFormTest(TestCase):
    """Тести форми CarBrandForm"""

    def test_valid_car_brand_form(self):
        """Тест валідної форми бренду"""
        form_data = {"name": "TestBrand"}
        form = CarBrandForm(data=form_data)
        self.assertTrue(form.is_valid())

@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class CarModelFormTest(TestCase):
    """Тести форми CarModelForm"""

    def setUp(self):
        self.brand = CarBrand.objects.create(name="BrandForm")

    def test_valid_car_model_form(self):
        """Тест валідної форми моделі"""
        form_data = {
            "brand": self.brand.id,
            "name": "ModelForm"
        }
        form = CarModelForm(data=form_data)
        self.assertTrue(form.is_valid())

@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class CarFormTest(TestCase):
    """Тести форми CarForm"""

    def setUp(self):
        self.brand = CarBrand.objects.create(name="TestBrand")
        self.model = CarModel.objects.create(brand=self.brand, name="TestModel")

    def test_valid_car_form(self):
        """Тест валідної форми автомобіля"""
        form_data = {
            "model": self.model.id,
            "year": 2023,
            "license_plate": "AA1234BB",
            "color": "Червоний",
            "mileage": 5000,
            "fuel_type": "petrol",
            "transmission": "manual",
            "price_per_minute": "2.50",
            "engine_capacity": "1.6",
            "power": 120,
            "seats": 5,
            "has_air_conditioning": True,
            "has_gps": False,
            "has_child_seat": False,
            "has_bluetooth": True,
            "has_usb": True,
            "status": "available",
            "current_latitude": "50.4501",
            "current_longitude": "30.5234",
            "insurance_valid_until": (date.today() + timedelta(days=365)).isoformat(),
            "technical_inspection_valid_until": (date.today() + timedelta(days=365)).isoformat(),
        }
        files_data = {
            "main_photo": get_test_image()
        }
        form = CarForm(data=form_data, files=files_data)
        self.assertTrue(form.is_valid())

@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class CarPhotoFormTest(TestCase):
    """Тести форми CarPhotoForm"""

    def setUp(self):
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
            main_photo=get_test_image()
        )

    def test_valid_car_photo_form(self):
        """Тест валідної форми фото автомобіля"""
        form_data = {
            "car": self.car.id,
            "caption": "Тестове фото"
        }
        files_data = {
            "photo": get_test_image()
        }
        form = CarPhotoForm(data=form_data, files=files_data)
        self.assertTrue(form.is_valid())

@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class CarReviewFormTest(TestCase):
    """Тести форми CarReviewForm"""

    def setUp(self):
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
            main_photo=get_test_image()
        )

    def test_valid_car_review_form(self):
        """Тест валідної форми відгуку"""
        form_data = {
            "car": self.car.id,
            "rating": 5,
            "comment": "Дуже хороший автомобіль"
        }
        form = CarReviewForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid())

class CarLocationFormTest(TestCase):
    """Тести форми CarLocationForm"""

    def test_valid_car_location_form(self):
        form_data = {
            "latitude": "50.4501",
            "longitude": "30.5234"
        }
        form = CarLocationForm(data=form_data)
        self.assertTrue(form.is_valid())

class CarStatusFormTest(TestCase):
    """Тести форми CarStatusForm"""

    def test_valid_car_status_form(self):
        form_data = {"status": "available"}
        form = CarStatusForm(data=form_data)
        self.assertTrue(form.is_valid())

class CarFilterFormTest(TestCase):
    """Тести форми CarFilterForm"""

    def test_valid_car_filter_form(self):
        form_data = {
            "min_year": 2010,
            "max_year": 2025,
            "fuel_type": "petrol",
            "transmission": "manual",
            "status": "available"
        }
        form = CarFilterForm(data=form_data)
        self.assertTrue(form.is_valid())

def tearDownModule():
    """Видалення тимчасової медіа-папки"""
    import shutil
    shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
