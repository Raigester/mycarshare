# -*- coding: utf-8 -*-
from datetime import date, timedelta
from decimal import Decimal
from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from PIL import Image

from cars.models import Car, CarBrand, CarModel


User = get_user_model()

def get_test_image(name="test.jpg"):
    """Створення тимчасового зображення для тестів"""
    img = Image.new("RGB", (100, 100), color="blue")
    buf = BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    return SimpleUploadedFile(name, buf.read(), content_type="image/jpeg")

class CarViewsTest(TestCase):
    """Тести представлень автомобілів"""

    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpass"
        )
        self.user = User.objects.create_user(
            username="user", email="user@example.com", password="userpass"
        )

        self.brand = CarBrand.objects.create(name="TestBrand")
        self.model = CarModel.objects.create(brand=self.brand, name="TestModel")
        self.car = Car.objects.create(
            model=self.model,
            year=2023,
            license_plate="TEST123",
            color="Red",
            mileage=10000,
            fuel_type="petrol",
            transmission="manual",
            price_per_minute=Decimal("2.50"),
            engine_capacity=Decimal("1.6"),
            power=120,
            seats=5,
            insurance_valid_until=date.today() + timedelta(days=365),
            technical_inspection_valid_until=date.today() + timedelta(days=365),
            main_photo=get_test_image()
        )


    def test_car_detail_view(self):
        """Тест перегляду деталей автомобіля"""
        response = self.client.get(reverse("car-detail", args=[self.car.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "car_detail.html")

    def test_car_create_view_admin(self):
        """Тест створення автомобіля адміном"""
        self.client.login(username="admin", password="adminpass")
        response = self.client.get(reverse("car-create"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "car_form.html")

    def test_car_update_view_admin(self):
        """Тест оновлення автомобіля адміном"""
        self.client.login(username="admin", password="adminpass")
        response = self.client.get(reverse("car-update", args=[self.car.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "car_form.html")

    def test_car_delete_view_admin(self):
        """Тест видалення автомобіля адміном"""
        self.client.login(username="admin", password="adminpass")
        response = self.client.get(reverse("car-delete", args=[self.car.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "car_confirm_delete.html")

    def test_cars_map_view(self):
        """Тест перегляду карти автомобілів"""
        response = self.client.get(reverse("cars-map"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "cars_map.html")

    def test_get_car_api_view(self):
        """Тест API отримання автомобіля"""
        response = self.client.get(reverse("car-api-detail", args=[self.car.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], self.car.id)

class CarBrandViewsTest(TestCase):
    """Тести представлень брендів автомобілів"""

    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_superuser(
            username="admin", email="admin@admin.com", password="adminpass"
        )
        self.brand = CarBrand.objects.create(name="BrandTest")

    def test_brand_detail_view(self):
        """Тест перегляду деталей бренду"""
        response = self.client.get(reverse("car-brand-detail", args=[self.brand.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "brand_detail.html")

class CarModelViewsTest(TestCase):
    """Тести представлень моделей автомобілів"""

    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_superuser(
            username="admin", email="admin@admin.com", password="adminpass"
        )
        self.brand = CarBrand.objects.create(name="BrandForModel")
        self.model = CarModel.objects.create(brand=self.brand, name="ModelTest")


    def test_model_detail_view(self):
        """Тест перегляду деталей моделі"""
        response = self.client.get(reverse("car-model-detail", args=[self.model.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "model_detail.html")

class CarPhotoViewsTest(TestCase):
    """Тести представлень фотографій автомобілів"""

    def setUp(self):
        self.client = Client()
        self.admin = User.objects.create_superuser(
            username="admin", email="admin@admin.com", password="adminpass"
        )
        self.brand = CarBrand.objects.create(name="PhotoBrand")
        self.model = CarModel.objects.create(brand=self.brand, name="PhotoModel")
        self.car = Car.objects.create(
            model=self.model,
            year=2023,
            license_plate="PHOTO123",
            color="Blue",
            mileage=5000,
            fuel_type="petrol",
            transmission="automatic",
            price_per_minute=Decimal("3.00"),
            seats=5,
            insurance_valid_until=date.today() + timedelta(days=365),
            technical_inspection_valid_until=date.today() + timedelta(days=365),
            main_photo=get_test_image()
        )

