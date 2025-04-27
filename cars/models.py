from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class CarBrand(models.Model):
    """Модель для брендів автомобілів"""
    
    name = models.CharField(max_length=100, unique=True)
    logo = models.ImageField(upload_to='brand_logos/', null=True, blank=True)
    
    def __str__(self):
        return self.name

class CarModel(models.Model):
    """Модель для моделей автомобілів"""
    
    brand = models.ForeignKey(CarBrand, on_delete=models.CASCADE, related_name='models')
    name = models.CharField(max_length=100)
    
    class Meta:
        unique_together = ('brand', 'name')
    
    def __str__(self):
        return f"{self.brand.name} {self.name}"

class Car(models.Model):
    """Модель для автомобілів"""
    
    STATUS_CHOICES = [
        ('available', 'Доступний'),
        ('busy', 'Зайнятий'),
        ('maintenance', 'На обслуговуванні'),
        ('inactive', 'Неактивний')
    ]

    FUEL_CHOICES = [
        ('petrol', 'Бензин'),
        ('diesel', 'Дизель'),
        ('electric', 'Електричний'),
        ('hybrid', 'Гібрид')
    ]

    TRANSMISSION_CHOICES = [
        ('manual', 'Механічна'),
        ('automatic', 'Автоматична')
    ]
    
    model = models.ForeignKey(CarModel, on_delete=models.CASCADE, related_name='cars')
    year = models.PositiveIntegerField()
    license_plate = models.CharField(max_length=20, unique=True)
    color = models.CharField(max_length=50)
    mileage = models.PositiveIntegerField(help_text="Пробіг у кілометрах")
    fuel_type = models.CharField(max_length=20, choices=FUEL_CHOICES)
    transmission = models.CharField(max_length=20, choices=TRANSMISSION_CHOICES)
    
    # Характеристики оренди
    price_per_minute = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    # Технічні характеристики
    engine_capacity = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)  # у літрах
    power = models.PositiveIntegerField(null=True, blank=True)  # у кінських силах
    seats = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    
    # Додаткові опції
    has_air_conditioning = models.BooleanField(default=True)
    has_gps = models.BooleanField(default=False)
    has_child_seat = models.BooleanField(default=False)
    has_bluetooth = models.BooleanField(default=False)
    has_usb = models.BooleanField(default=True)
    
    # Статус і місцезнаходження
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    current_latitude = models.CharField(max_length=255, blank=True)
    current_longitude = models.CharField(max_length=255, blank=True)
    
    # Медіа
    main_photo = models.ImageField(upload_to='car_photos/')
    
    # Рейтинг
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    
    # Інформація про обслуговування
    insurance_valid_until = models.DateField()
    technical_inspection_valid_until = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.model} ({self.license_plate})"

class CarPhoto(models.Model):
    """Модель для додаткових фотографій автомобілів"""
    
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='photos')
    photo = models.ImageField(upload_to='car_photos/')
    caption = models.CharField(max_length=200, blank=True)
    
    def __str__(self):
        return f"Фото {self.id} для {self.car}"

class CarReview(models.Model):
    """Модель для відгуків про автомобілі"""
    
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('car', 'user')
    
    def __str__(self):
        return f"Відгук від {self.user.username} для {self.car}"
