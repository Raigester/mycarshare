from decimal import Decimal
import os
import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from utils.data_validation import validate_phone_number

# Функція для генерації унікального шляху для фото профілю
def profile_picture_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    return os.path.join('profile_pictures', filename)

# Функція для генерації унікального шляху для фото верифікації водійських прав
def license_image_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    return os.path.join('license_verifications', filename)

class User(AbstractUser):
    """Extended user model"""
    
    phone_number = models.CharField(validators=[validate_phone_number], max_length=17, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to=profile_picture_upload_path, null=True, blank=True)
    
    # Driver verification data
    driver_license_number = models.CharField(max_length=20, blank=True)
    driver_license_expiry = models.DateField(null=True, blank=True)
    is_verified_driver = models.BooleanField(default=False)
    
    # User rating
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    
    # Additional fields
    is_blocked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.username

class DriverLicenseVerification(models.Model):
    """Model for driver license verification"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='license_verifications')
    front_image = models.ImageField(upload_to=license_image_upload_path)
    back_image = models.ImageField(upload_to=license_image_upload_path)
    selfie_with_license = models.ImageField(upload_to=license_image_upload_path)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'На розгляді'),
            ('approved', 'Схвалено'),
            ('rejected', 'Відхилено')
        ],
        default='pending'
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.status}"

class UserBalance(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='balance')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    last_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Balance for {self.user.username}: {self.amount}"
