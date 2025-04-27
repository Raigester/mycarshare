import datetime

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Booking(models.Model):
    """Модель для бронювання автомобілів"""

    STATUS_CHOICES = [
        ("pending", "Очікує підтвердження"),
        ("confirmed", "Підтверджено"),
        ("active", "Активний"),
        ("completed", "Завершено"),
        ("cancelled", "Скасовано")
    ]

    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="bookings"
    )  # Користувач, який створив бронювання
    car = models.ForeignKey(
        "cars.Car",
        on_delete=models.CASCADE,
        related_name="bookings"
    )  # Автомобіль, який заброньовано

    # Час бронювання
    start_time = models.DateTimeField()  # Час початку бронювання
    end_time = models.DateTimeField(null=True, blank=True)  # Час завершення бронювання (може бути порожнім)

    # Локації
    pickup_location = models.CharField(max_length=255, blank=True)  # Локація, де забирають автомобіль
    return_location = models.CharField(max_length=255, blank=True)  # Локація, де повертають автомобіль

    # Статус та інформація
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")  # Статус бронювання
    total_price = models.DecimalField(max_digits=10, decimal_places=2)  # Загальна вартість бронювання

    # Системна інформація
    created_at = models.DateTimeField(auto_now_add=True)  # Дата створення бронювання
    updated_at = models.DateTimeField(auto_now=True)  # Дата останнього оновлення бронювання

    # Інформація про оплату
    last_billing_time = models.DateTimeField(null=True, blank=True)  # Час останнього виставлення рахунку
    minutes_billed = models.PositiveIntegerField(default=0)  # Кількість хвилин, за які виставлено рахунок

    def __str__(self):
        return f"Booking {self.id} - {self.car} ({self.status})"

    def clean(self):
        """Валідація моделі"""

        # Перевірка, що час початку раніше за час завершення
        if self.end_time:
            if self.start_time >= self.end_time:
                raise ValidationError("Час початку має бути раніше за час завершення")

        # Перевірка лише при створенні нового бронювання (якщо немає первинного ключа)
        # Переконайтеся, що час початку оренди знаходиться в майбутньому (з допуском у 2 секунди)
        if self.pk is None:
            if self.start_time and self.start_time <= timezone.now() - datetime.timedelta(seconds=2):
                raise ValidationError("Час початку має бути в майбутньому")

        # Перевірка на перетин бронювань у той самий період
        if self.end_time:
            overlapping_bookings = Booking.objects.exclude(id=self.id).filter(
                car=self.car,
                status__in=["pending", "confirmed", "active"],
                start_time__lt=self.end_time,
                end_time__gt=self.start_time
            )

            if overlapping_bookings.exists():
                raise ValidationError("Автомобіль вже заброньовано на цей період")

    def save(self, *args, **kwargs):
        # Виконати валідацію перед збереженням
        self.clean()

        # Якщо це нове бронювання і статус підтверджений, оновити статус автомобіля
        if not self.id and self.status in ["confirmed", "active"]:
            self.car.status = "busy"
            self.car.save()

        super().save(*args, **kwargs)

class BookingHistory(models.Model):
    """Модель для історії бронювань (для відстеження змін)"""

    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name="history"
    )  # Бронювання, до якого належить запис історії
    status = models.CharField(max_length=20, choices=Booking.STATUS_CHOICES)  # Статус бронювання на момент запису
    timestamp = models.DateTimeField(auto_now_add=True)  # Час створення запису історії
    notes = models.TextField(blank=True)  # Додаткові примітки до запису історії

    def __str__(self):
        return f"History {self.booking.id} - {self.status} ({self.timestamp})"
