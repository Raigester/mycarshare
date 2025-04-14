from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

class User(AbstractUser):
    """Extended user model"""
    
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    
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
    front_image = models.ImageField(upload_to='license_verifications/')
    back_image = models.ImageField(upload_to='license_verifications/')
    selfie_with_license = models.ImageField(upload_to='license_verifications/')
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending review'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected')
        ],
        default='pending'
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.status}"
