from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class CarBrand(models.Model):
    """Модель для брендів автомобілів"""

    name = models.CharField(max_length=100, unique=True)  # Назва бренду автомобіля
    logo = models.ImageField(upload_to="brand_logos/", null=True, blank=True)  # Логотип бренду (може бути порожнім)

    def __str__(self):
        return self.name

class CarModel(models.Model):
    """Модель для моделей автомобілів"""

    brand = models.ForeignKey(
        CarBrand,
        on_delete=models.CASCADE,
        related_name="models"
    )  # Бренд, до якого належить модель
    name = models.CharField(max_length=100)  # Назва моделі автомобіля

    class Meta:
        unique_together = ("brand", "name")  # Унікальність моделі для кожного бренду

    def __str__(self):
        return f"{self.brand.name} {self.name}"

class Car(models.Model):
    """Модель для автомобілів"""

    STATUS_CHOICES = [
        ("available", "Доступний"),
        ("busy", "Зайнятий"),
        ("maintenance", "На обслуговуванні"),
        ("inactive", "Неактивний")
    ]

    FUEL_CHOICES = [
        ("petrol", "Бензин"),
        ("diesel", "Дизель"),
        ("electric", "Електричний"),
        ("hybrid", "Гібрид")
    ]

    TRANSMISSION_CHOICES = [
        ("manual", "Механічна"),
        ("automatic", "Автоматична")
    ]

    model = models.ForeignKey(CarModel, on_delete=models.CASCADE, related_name="cars")  # Модель автомобіля
    year = models.PositiveIntegerField()  # Рік випуску автомобіля
    license_plate = models.CharField(max_length=20, unique=True)  # Номерний знак автомобіля
    color = models.CharField(max_length=50)  # Колір автомобіля
    mileage = models.PositiveIntegerField(help_text="Пробіг у кілометрах")  # Пробіг автомобіля
    fuel_type = models.CharField(max_length=20, choices=FUEL_CHOICES)  # Тип палива
    transmission = models.CharField(max_length=20, choices=TRANSMISSION_CHOICES)  # Тип трансмісії

    # Характеристики оренди
    price_per_minute = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00")
    )  # Ціна оренди за хвилину

    # Технічні характеристики
    engine_capacity = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        null=True,
        blank=True
    )  # Об'єм двигуна у літрах
    power = models.PositiveIntegerField(null=True, blank=True)  # Потужність двигуна у кінських силах
    seats = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10)
        ]
    )  # Кількість місць у автомобілі

    # Додаткові опції
    has_air_conditioning = models.BooleanField(default=True)  # Наявність кондиціонера
    has_gps = models.BooleanField(default=False)  # Наявність GPS
    has_child_seat = models.BooleanField(default=False)  # Наявність дитячого крісла
    has_bluetooth = models.BooleanField(default=False)  # Наявність Bluetooth
    has_usb = models.BooleanField(default=True)  # Наявність USB

    # Статус і місцезнаходження
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="available")  # Статус автомобіля
    current_latitude = models.CharField(max_length=255, blank=True)  # Поточна широта автомобіля
    current_longitude = models.CharField(max_length=255, blank=True)  # Поточна довгота автомобіля

    # Медіа
    main_photo = models.ImageField(upload_to="car_photos/")  # Головне фото автомобіля

    # Рейтинг
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)  # Рейтинг автомобіля

    # Інформація про обслуговування
    insurance_valid_until = models.DateField()  # Дата закінчення дії страховки
    technical_inspection_valid_until = models.DateField()  # Дата закінчення технічного огляду
    created_at = models.DateTimeField(auto_now_add=True)  # Дата створення запису
    updated_at = models.DateTimeField(auto_now=True)  # Дата останнього оновлення запису

    def __str__(self):
        return f"{self.model} ({self.license_plate})"

class CarPhoto(models.Model):
    """Модель для додаткових фотографій автомобілів"""

    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="photos")  # Автомобіль, до якого належить фото
    photo = models.ImageField(upload_to="car_photos/")  # Шлях для збереження фотографії
    caption = models.CharField(max_length=200, blank=True)  # Підпис до фотографії

    def __str__(self):
        return f"Фото {self.id} для {self.car}"

class CarReview(models.Model):
    """Модель для відгуків про автомобілі"""

    car = models.ForeignKey(
        Car,
        on_delete=models.CASCADE,
        related_name="reviews"
    )  # Автомобіль, до якого належить відгук
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)  # Користувач, який залишив відгук
    rating = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
    )  # Рейтинг автомобіля (від 1 до 5)
    comment = models.TextField()  # Текст відгуку
    created_at = models.DateTimeField(auto_now_add=True)  # Дата створення відгуку

    class Meta:
        unique_together = ("car", "user")  # Унікальність відгуку для пари автомобіль-користувач

    def __str__(self):
        return f"Відгук від {self.user.username} для {self.car}"
