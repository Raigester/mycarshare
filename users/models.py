import os
import uuid
from decimal import Decimal

from django.contrib.auth.models import AbstractUser
from django.db import models

from utils.data_validation import validate_phone_number


# Функція для генерації унікального шляху для фото профілю
def profile_picture_upload_path(instance, filename):
    """Генерує унікальний шлях для збереження фото профілю"""
    ext = filename.split(".")[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    return os.path.join("profile_pictures", filename)

# Функція для генерації унікального шляху для фото верифікації водійських прав
def license_image_upload_path(instance, filename):
    """Генерує унікальний шлях для збереження фото верифікації водійських прав"""
    ext = filename.split(".")[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    return os.path.join("license_verifications", filename)

class User(AbstractUser):
    """Розширена модель користувача"""

    email = models.EmailField(unique=True) # Електронна пошта користувача
    phone_number = models.CharField(
        validators=[validate_phone_number],
        max_length=17,
        blank=True
    )  # Номер телефону користувача
    date_of_birth = models.DateField(null=True, blank=True)  # Дата народження
    profile_picture = models.ImageField(upload_to=profile_picture_upload_path, null=True, blank=True)  # Фото профілю

    # Дані для верифікації водія
    driver_license_number = models.CharField(max_length=20, blank=True)  # Номер водійського посвідчення
    driver_license_expiry = models.DateField(null=True, blank=True)  # Дата закінчення дії водійського посвідчення
    is_verified_driver = models.BooleanField(default=False)  # Чи є користувач верифікованим водієм

    # Рейтинг користувача
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)  # Рейтинг користувача

    # Додаткові поля
    is_blocked = models.BooleanField(default=False)  # Чи заблокований користувач
    created_at = models.DateTimeField(auto_now_add=True)  # Дата створення запису
    updated_at = models.DateTimeField(auto_now=True)  # Дата останнього оновлення запису
    is_email_verified = models.BooleanField(default=False) # Чи підтверджена електронна пошта
    email_verification_token = models.UUIDField(default=uuid.uuid4, editable=False) # Токен для підтвердження пошти

    def __str__(self):
        """Повертає ім'я користувача як рядок"""
        return self.username

class DriverLicenseVerification(models.Model):
    """Модель для верифікації водійських прав"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="license_verifications"
    )  # Зв'язок із користувачем
    front_image = models.ImageField(upload_to=license_image_upload_path)  # Фото передньої сторони посвідчення
    back_image = models.ImageField(upload_to=license_image_upload_path)  # Фото зворотної сторони посвідчення
    selfie_with_license = models.ImageField(upload_to=license_image_upload_path)  # Селфі з посвідченням
    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "На розгляді"),  # Статус: на розгляді
            ("approved", "Схвалено"),  # Статус: схвалено
            ("rejected", "Відхилено")  # Статус: відхилено
        ],
        default="pending"
    )
    comment = models.TextField(blank=True)  # Коментар адміністратора
    created_at = models.DateTimeField(auto_now_add=True)  # Дата створення запису
    updated_at = models.DateTimeField(auto_now=True)  # Дата останнього оновлення запису

    def __str__(self):
        """Повертає статус верифікації як рядок"""
        return f"{self.user.username} - {self.status}"

class UserBalance(models.Model):
    """Модель для зберігання балансу користувача"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="balance")  # Зв'язок із користувачем
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))  # Баланс користувача
    last_updated = models.DateTimeField(auto_now=True)  # Дата останнього оновлення балансу

    def __str__(self):
        """Повертає інформацію про баланс як рядок"""
        return f"Баланс для {self.user.username}: {self.amount}"
