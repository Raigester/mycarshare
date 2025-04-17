from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class CarBrand(models.Model):
    """Model for car brands"""
    
    name = models.CharField(max_length=100, unique=True)
    logo = models.ImageField(upload_to='brand_logos/', null=True, blank=True)
    
    def __str__(self):
        return self.name

class CarModel(models.Model):
    """Model for car models"""
    
    brand = models.ForeignKey(CarBrand, on_delete=models.CASCADE, related_name='models')
    name = models.CharField(max_length=100)
    
    class Meta:
        unique_together = ('brand', 'name')
    
    def __str__(self):
        return f"{self.brand.name} {self.name}"

class Car(models.Model):
    """Model for cars"""
    
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('busy', 'Busy'),
        ('maintenance', 'Under maintenance'),
        ('inactive', 'Inactive')
    ]
    
    FUEL_CHOICES = [
        ('petrol', 'Petrol'),
        ('diesel', 'Diesel'),
        ('electric', 'Electric'),
        ('hybrid', 'Hybrid')
    ]
    
    TRANSMISSION_CHOICES = [
        ('manual', 'Manual'),
        ('automatic', 'Automatic')
    ]
    
    model = models.ForeignKey(CarModel, on_delete=models.CASCADE, related_name='cars')
    year = models.PositiveIntegerField()
    license_plate = models.CharField(max_length=20, unique=True)
    color = models.CharField(max_length=50)
    mileage = models.PositiveIntegerField(help_text="Mileage in kilometers")
    fuel_type = models.CharField(max_length=20, choices=FUEL_CHOICES)
    transmission = models.CharField(max_length=20, choices=TRANSMISSION_CHOICES)
    
    # Rental characteristics
    price_per_minute = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2)
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2)
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Technical specifications
    engine_capacity = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)  # in liters
    power = models.PositiveIntegerField(null=True, blank=True)  # in horsepower
    seats = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    
    # Additional options
    has_air_conditioning = models.BooleanField(default=True)
    has_gps = models.BooleanField(default=False)
    has_child_seat = models.BooleanField(default=False)
    has_bluetooth = models.BooleanField(default=False)
    has_usb = models.BooleanField(default=True)
    
    # Status and location
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    current_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    current_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Media
    main_photo = models.ImageField(upload_to='car_photos/')
    
    # Rating
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    
    # Service information
    insurance_valid_until = models.DateField()
    technical_inspection_valid_until = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.model} ({self.license_plate})"

class CarPhoto(models.Model):
    """Model for additional car photos"""
    
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='photos')
    photo = models.ImageField(upload_to='car_photos/')
    caption = models.CharField(max_length=200, blank=True)
    
    def __str__(self):
        return f"Photo {self.id} for {self.car}"

class CarReview(models.Model):
    """Model for car reviews"""
    
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('car', 'user')
    
    def __str__(self):
        return f"Review by {self.user.username} for {self.car}"
