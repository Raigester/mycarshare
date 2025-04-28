# -*- coding: utf-8 -*-
import os
import tempfile
from datetime import date
from decimal import Decimal
from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from PIL import Image

from users.models import DriverLicenseVerification, User, UserBalance


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
class UserRegistrationViewTest(TestCase):
    """Тестування представлення реєстрації користувача"""

    def setUp(self):
        """Налаштування тестового середовища"""
        self.client = Client()
        self.register_url = reverse("register")

    def test_registration_view_get(self):
        """Тест GET-запиту на сторінку реєстрації"""
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "register.html")

    def test_registration_view_post_success(self):
        """Тест успішної реєстрації користувача"""
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password1": "SecurePassword123",
            "password2": "SecurePassword123",
            "first_name": "New",
            "last_name": "User",
        }
        response = self.client.post(self.register_url, user_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("login"))
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_registration_view_post_invalid_data(self):
        """Тест реєстрації з неправильними даними"""
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password1": "short",
            "password2": "short",
        }
        response = self.client.post(self.register_url, user_data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="newuser").exists())


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class CustomLoginViewTest(TestCase):
    """Тестування представлення логіну користувача"""

    def setUp(self):
        """Налаштування тестового середовища"""
        self.client = Client()
        self.login_url = reverse("login")
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword123",
        )

    def test_login_view_get(self):
        """Тест GET-запиту на сторінку логіну"""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login.html")

    def test_login_view_post_success(self):
        """Тест успішного логіну"""
        login_data = {
            "username": "testuser",
            "password": "testpassword123",
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("profile"))

    def test_login_view_already_authenticated(self):
        """Тест логіну вже аутентифікованого користувача"""
        self.client.login(username="testuser", password="testpassword123")
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("profile"))


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class UserProfileViewTest(TestCase):
    """Тестування представлення профілю користувача"""

    def setUp(self):
        """Налаштування тестового середовища"""
        self.client = Client()
        self.profile_url = reverse("profile")
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword123",
            first_name="Test",
            last_name="User",
        )

    def test_profile_view_unauthenticated(self):
        """Тест доступу до профілю неаутентифікованого користувача"""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 302)
        # Перевіряємо, що URL починається з '/login/' або містить 'login'
        login_path = reverse("login")
        self.assertIn(login_path, response.url)

    def test_profile_view_authenticated(self):
        """Тест доступу до профілю аутентифікованого користувача"""
        self.client.login(username="testuser", password="testpassword123")
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "profile.html")

    def test_profile_update(self):
        """Тест оновлення профілю користувача"""
        self.client.login(username="testuser", password="testpassword123")
        update_data = {
            "first_name": "Updated",
            "last_name": "Name",
            "phone_number": "+380991234567",
            "date_of_birth": "1990-01-01",
        }
        response = self.client.post(self.profile_url, update_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.profile_url)

        # Оновлення користувача з бази даних
        updated_user = User.objects.get(id=self.user.id)
        self.assertEqual(updated_user.first_name, "Updated")
        self.assertEqual(updated_user.last_name, "Name")
        self.assertEqual(updated_user.phone_number, "+380991234567")
        self.assertEqual(updated_user.date_of_birth, date(1990, 1, 1))


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ChangePasswordViewTest(TestCase):
    """Тестування представлення зміни пароля"""

    def setUp(self):
        """Налаштування тестового середовища"""
        self.client = Client()
        self.change_password_url = reverse("change-password")
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="oldpassword123",
        )

    def test_change_password_view_unauthenticated(self):
        """Тест доступу до зміни пароля неаутентифікованим користувачем"""
        response = self.client.get(self.change_password_url)
        self.assertEqual(response.status_code, 302)
        # Перевіряємо, що URL починається з '/login/' або містить 'login'
        login_path = reverse("login")
        self.assertIn(login_path, response.url)

    def test_change_password_view_authenticated(self):
        """Тест доступу до зміни пароля аутентифікованим користувачем"""
        self.client.login(username="testuser", password="oldpassword123")
        response = self.client.get(self.change_password_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "change_password.html")

    def test_change_password_success(self):
        """Тест успішної зміни пароля"""
        self.client.login(username="testuser", password="oldpassword123")
        password_data = {
            "old_password": "oldpassword123",
            "new_password1": "newpassword123",
            "new_password2": "newpassword123",
        }
        response = self.client.post(self.change_password_url, password_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("profile"))

        # Перевіряємо, що можемо залогінитися з новим паролем
        self.client.logout()
        self.assertTrue(self.client.login(username="testuser", password="newpassword123"))


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class DriverLicenseVerificationCreateViewTest(TestCase):
    """Тестування представлення створення заявки на верифікацію водійських прав"""

    def setUp(self):
        """Налаштування тестового середовища"""
        self.client = Client()
        self.verification_create_url = reverse("verification-create")
        self.verification_list_url = reverse("verification-list")
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword123",
        )
        # Створюємо справжні тестові зображення
        self.front_image = get_temporary_image("front.png")
        self.back_image = get_temporary_image("back.png")
        self.selfie_image = get_temporary_image("selfie.png")

    def test_verification_create_view_authenticated(self):
        """Тест доступу до створення заявки аутентифікованим користувачем"""
        self.client.login(username="testuser", password="testpassword123")
        response = self.client.get(self.verification_create_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "driver_verification_form.html")

    def test_verification_create_success(self):
        """Тест успішного створення заявки на верифікацію"""
        self.client.login(username="testuser", password="testpassword123")

        # Оновіть зображення перед кожним тестом
        front_image = get_temporary_image("front_new.png")
        back_image = get_temporary_image("back_new.png")
        selfie_image = get_temporary_image("selfie_new.png")

        verification_data = {
            "front_image": front_image,
            "back_image": back_image,
            "selfie_with_license": selfie_image,
        }

        response = self.client.post(self.verification_create_url, verification_data)

        # Для діагностики виведіть сторінку, якщо статус не 302
        if response.status_code != 302:
            print(f"Статус відповіді: {response.status_code}")
            print(f"Контент відповіді: {response.content.decode('utf-8')[:500]}...")

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.verification_list_url)
        self.assertTrue(DriverLicenseVerification.objects.filter(user=self.user).exists())

    def test_verification_create_with_existing_active_verification(self):
        """Тест створення заявки, коли вже є активна заявка"""
        self.client.login(username="testuser", password="testpassword123")

        # Створюємо справжні тестові зображення для існуючої верифікації
        front_image = get_temporary_image("front_existing.png")
        back_image = get_temporary_image("back_existing.png")
        selfie_image = get_temporary_image("selfie_existing.png")

        # Спочатку створимо заявку
        DriverLicenseVerification.objects.create(
            user=self.user,
            front_image=front_image,
            back_image=back_image,
            selfie_with_license=selfie_image,
            status="pending"
        )

        response = self.client.get(self.verification_create_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.verification_list_url)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class DriverLicenseVerificationListViewTest(TestCase):
    """Тестування представлення списку заявок на верифікацію"""

    def setUp(self):
        """Налаштування тестового середовища"""
        self.client = Client()
        self.verification_list_url = reverse("verification-list")
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword123",
        )

    def test_verification_list_view_unauthenticated(self):
        """Тест доступу до списку заявок неаутентифікованим користувачем"""
        response = self.client.get(self.verification_list_url)
        self.assertEqual(response.status_code, 302)
        # Перевіряємо, що URL починається з '/login/' або містить 'login'
        login_path = reverse("login")
        self.assertIn(login_path, response.url)

    def test_verification_list_view_authenticated(self):
        """Тест доступу до списку заявок аутентифікованим користувачем"""
        self.client.login(username="testuser", password="testpassword123")
        response = self.client.get(self.verification_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "driver_verification_list.html")


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class AdminVerificationViewsTest(TestCase):
    """Тестування представлень адміністратора для верифікації"""

    def setUp(self):
        """Налаштування тестового середовища"""
        self.client = Client()
        self.admin_list_url = reverse("admin-verification-list")

        # Створюємо адміністратора
        self.admin_user = User.objects.create_user(
            username="adminuser",
            email="admin@example.com",
            password="adminpassword123",
            is_staff=True
        )

        # Створюємо звичайного користувача
        self.regular_user = User.objects.create_user(
            username="regularuser",
            email="regular@example.com",
            password="regularpassword123",
        )

        # Створюємо заявку на верифікацію
        front_image = get_temporary_image("admin_front.png")
        back_image = get_temporary_image("admin_back.png")
        selfie_image = get_temporary_image("admin_selfie.png")

        self.verification = DriverLicenseVerification.objects.create(
            user=self.regular_user,
            front_image=front_image,
            back_image=back_image,
            selfie_with_license=selfie_image,
            status="pending"
        )

        self.detail_url = reverse("admin-verification-detail", kwargs={"pk": self.verification.pk})

    def test_admin_list_view_access(self):
        """Тест доступу до списку заявок адміністратором і звичайним користувачем"""
        # Звичайний користувач не повинен мати доступу
        self.client.login(username="regularuser", password="regularpassword123")
        response = self.client.get(self.admin_list_url)
        self.assertEqual(response.status_code, 403)  # Forbidden

        # Адміністратор повинен мати доступ
        self.client.logout()
        self.client.login(username="adminuser", password="adminpassword123")
        response = self.client.get(self.admin_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin_verification_list.html")

    def test_admin_detail_view_access(self):
        """Тест доступу до деталей заявки адміністратором і звичайним користувачем"""
        # Звичайний користувач не повинен мати доступу
        self.client.login(username="regularuser", password="regularpassword123")
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 403)  # Forbidden

        # Адміністратор повинен мати доступ
        self.client.logout()
        self.client.login(username="adminuser", password="adminpassword123")
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "admin_verification_detail.html")

    def test_admin_update_verification_approve(self):
        """Тест затвердження заявки адміністратором"""
        self.client.login(username="adminuser", password="adminpassword123")
        update_data = {
            "status": "approved",
            "comment": "License verification approved",
        }
        response = self.client.post(self.detail_url, update_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.admin_list_url)

        # Перевіряємо, що статус заявки змінився і користувач став верифікованим
        verification = DriverLicenseVerification.objects.get(pk=self.verification.pk)
        self.assertEqual(verification.status, "approved")

        user = User.objects.get(pk=self.regular_user.pk)
        self.assertTrue(user.is_verified_driver)

    def test_admin_update_verification_reject(self):
        """Тест відхилення заявки адміністратором"""
        self.client.login(username="adminuser", password="adminpassword123")
        update_data = {
            "status": "rejected",
            "comment": "License verification rejected",
        }
        response = self.client.post(self.detail_url, update_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.admin_list_url)

        # Перевіряємо, що статус заявки змінився, але користувач не став верифікованим
        verification = DriverLicenseVerification.objects.get(pk=self.verification.pk)
        self.assertEqual(verification.status, "rejected")

        user = User.objects.get(pk=self.regular_user.pk)
        self.assertFalse(user.is_verified_driver)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class UserBalanceViewTest(TestCase):
    """Тестування представлення балансу користувача"""

    def setUp(self):
        """Налаштування тестового середовища"""
        self.client = Client()
        self.balance_url = reverse("balance")
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword123",
        )

    def test_balance_view_unauthenticated(self):
        """Тест доступу до балансу неаутентифікованим користувачем"""
        response = self.client.get(self.balance_url)
        self.assertEqual(response.status_code, 302)
        # Перевіряємо, що URL починається з '/login/' або містить 'login'
        login_path = reverse("login")
        self.assertIn(login_path, response.url)

    def test_balance_view_authenticated(self):
        """Тест доступу до балансу аутентифікованим користувачем"""
        self.client.login(username="testuser", password="testpassword123")
        response = self.client.get(self.balance_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "balance.html")

        # Перевіряємо, що баланс був автоматично створений
        self.assertTrue(UserBalance.objects.filter(user=self.user).exists())

    def test_add_balance(self):
        """Тест додавання коштів на баланс"""
        self.client.login(username="testuser", password="testpassword123")

        # Спочатку переконаємося, що баланс нульовий або не існує
        balance, created = UserBalance.objects.get_or_create(user=self.user)
        balance.amount = Decimal("0.00")
        balance.save()

        # Додаємо кошти на баланс
        balance_data = {
            "amount": "100.50",
        }
        response = self.client.post(self.balance_url, balance_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.balance_url)

        # Перевіряємо, що баланс оновився
        updated_balance = UserBalance.objects.get(user=self.user)
        self.assertEqual(updated_balance.amount, Decimal("100.50"))


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
