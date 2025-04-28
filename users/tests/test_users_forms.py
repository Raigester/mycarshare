# -*- coding: utf-8 -*-
import os
import tempfile
from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from PIL import Image

from users.forms import (
    AdminVerificationForm,
    BalanceAddForm,
    DriverLicenseVerificationForm,
    UserProfileUpdateForm,
    UserRegistrationForm,
)
from users.models import User


# Створюємо тимчасову директорію для медіа-файлів під час тестування
TEMP_MEDIA_ROOT = tempfile.mkdtemp()

# Функція для створення тестового зображення
def get_temporary_image(name="test.png"):
    """Створює тестове зображення для використання в тестах."""
    size = (200, 200)
    color = (255, 0, 0)  # червоний
    image_file = BytesIO()
    image = Image.new("RGB", size, color)
    image.save(image_file, "png")
    image_file.seek(0)
    return SimpleUploadedFile(name, image_file.read(), content_type="image/png")


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class UserRegistrationFormTest(TestCase):
    """Тестування форми реєстрації користувача"""

    def setUp(self):
        """Налаштування тестового середовища"""
        User.objects.create_user(
            username="existinguser",
            email="existing@example.com",
            password="testpassword123",
        )

    def test_registration_form_valid_data(self):
        """Тест валідації форми з коректними даними"""
        form_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password1": "SecurePassword123",
            "password2": "SecurePassword123",
            "first_name": "New",
            "last_name": "User",
            "phone_number": "+380991234567",
            "date_of_birth": "1990-01-01",
        }
        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_registration_form_email_already_exists(self):
        """Тест валідації форми з існуючим email"""
        form_data = {
            "username": "anotheruser",
            "email": "existing@example.com",  # Вже існуючий email
            "password1": "SecurePassword123",
            "password2": "SecurePassword123",
            "first_name": "Another",
            "last_name": "User",
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_registration_form_passwords_not_matching(self):
        """Тест валідації форми з паролями, що не співпадають"""
        form_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password1": "SecurePassword123",
            "password2": "DifferentPassword123",
            "first_name": "New",
            "last_name": "User",
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class UserProfileUpdateFormTest(TestCase):
    """Тестування форми оновлення профілю користувача"""

    def test_profile_update_form_valid_data(self):
        """Тест валідації форми з коректними даними"""
        form_data = {
            "first_name": "Updated",
            "last_name": "User",
            "phone_number": "+380991234567",
            "date_of_birth": "1990-01-01",
        }
        form = UserProfileUpdateForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_profile_update_form_with_profile_picture(self):
        """Тест валідації форми з фото профілю"""
        # Створюємо справжнє тестове зображення
        image = get_temporary_image("profile.png")

        form_data = {
            "first_name": "Updated",
            "last_name": "User",
            "phone_number": "+380991234567",
            "date_of_birth": "1990-01-01",
        }
        file_data = {
            "profile_picture": image,
        }

        form = UserProfileUpdateForm(data=form_data, files=file_data)

        # Виводимо помилки форми для аналізу
        if not form.is_valid():
            print(f"Помилки форми UserProfileUpdateForm: {form.errors}")

        self.assertTrue(form.is_valid())


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class DriverLicenseVerificationFormTest(TestCase):
    """Тестування форми верифікації водійських прав"""

    def test_driver_verification_form_valid_data(self):
        """Тест валідації форми з коректними даними"""
        # Створюємо справжні тестові зображення
        front_image = get_temporary_image("front.png")
        back_image = get_temporary_image("back.png")
        selfie_image = get_temporary_image("selfie.png")

        file_data = {
            "front_image": front_image,
            "back_image": back_image,
            "selfie_with_license": selfie_image,
        }

        form = DriverLicenseVerificationForm(files=file_data)

        # Виводимо помилки форми для аналізу
        if not form.is_valid():
            print(f"Помилки форми DriverLicenseVerificationForm: {form.errors}")

        self.assertTrue(form.is_valid())

    def test_driver_verification_form_missing_files(self):
        """Тест валідації форми з відсутніми файлами"""
        form = DriverLicenseVerificationForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn("front_image", form.errors)
        self.assertIn("back_image", form.errors)
        self.assertIn("selfie_with_license", form.errors)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class AdminVerificationFormTest(TestCase):
    """Тестування форми адміністратора для верифікації водійських прав"""

    def test_admin_verification_form_valid_data(self):
        """Тест валідації форми з коректними даними"""
        form_data = {
            "status": "approved",
            "comment": "Verification approved",
        }
        form = AdminVerificationForm(data=form_data)
        self.assertTrue(form.is_valid())


class BalanceAddFormTest(TestCase):
    """Тестування форми додавання коштів на баланс"""

    def test_balance_add_form_valid_data(self):
        """Тест валідації форми з коректною сумою"""
        form_data = {
            "amount": "100.50",
        }
        form = BalanceAddForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_balance_add_form_negative_amount(self):
        """Тест валідації форми з від'ємною сумою"""
        form_data = {
            "amount": "-10.00",
        }
        form = BalanceAddForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("amount", form.errors)

    def test_balance_add_form_zero_amount(self):
        """Тест валідації форми з нульовою сумою"""
        form_data = {
            "amount": "0.00",
        }
        form = BalanceAddForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("amount", form.errors)


# Видаляємо всі тимчасові файли після виконання тестів
def tearDownModule():
    print(f"Прибирання тимчасових файлів з {TEMP_MEDIA_ROOT}")
    for root, dirs, files in os.walk(TEMP_MEDIA_ROOT, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    if os.path.exists(TEMP_MEDIA_ROOT):
        os.rmdir(TEMP_MEDIA_ROOT)
