from django.utils import timezone
from rest_framework import serializers

from .models import Booking, BookingHistory


class BookingSerializer(serializers.ModelSerializer):
    """Серіалізатор для бронювань"""

    car_details = serializers.SerializerMethodField()
    user_name = serializers.ReadOnlyField(source="user.get_full_name")
    duration_hours = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = "__all__"
        read_only_fields = ("user", "total_price", "status", "created_at", "updated_at")

    def get_car_details(self, obj):
        """Отримати базову інформацію про автомобіль"""
        car = obj.car
        return {
            "id": car.id,
            "brand": car.model.brand.name,
            "model": car.model.name,
            "license_plate": car.license_plate,
            "main_photo": car.main_photo.url if car.main_photo else None
        }

    def get_duration_hours(self, obj):
        """Розрахувати тривалість бронювання в годинах"""
        duration = obj.end_time - obj.start_time
        hours = duration.total_seconds() / 3600
        return round(hours, 1)

    def validate(self, data):
        """Додаткова валідація даних"""

        # Перевірка доступності автомобіля
        car = data.get("car")
        if car and car.status not in ["available"]:
            raise serializers.ValidationError({"car": "Автомобіль недоступний для бронювання"})

        # Перевірка валідності часу
        start_time = data.get("start_time")
        end_time = data.get("end_time")

        if start_time and end_time:
            # Переконатися, що час початку раніше за час завершення
            if start_time >= end_time:
                raise serializers.ValidationError({"end_time": "Час завершення має бути пізніше за час початку"})

            # Переконатися, що час початку знаходиться в майбутньому
            if start_time <= timezone.now():
                raise serializers.ValidationError({"start_time": "Час початку має бути в майбутньому"})

            # Перевірка на перетин бронювань
            if car:
                booking_id = self.instance.id if self.instance else None
                overlapping_bookings = Booking.objects.exclude(id=booking_id).filter(
                    car=car,
                    status__in=["pending", "confirmed", "active"],
                    start_time__lt=end_time,
                    end_time__gt=start_time
                )

                if overlapping_bookings.exists():
                    raise serializers.ValidationError(
                        {"car": "Автомобіль вже заброньовано на цей період"}
                    )

        return data

    def create(self, validated_data):
        # Додати користувача та розраховану ціну
        validated_data["user"] = self.context["request"].user
        validated_data["total_price"] = self.context.get("total_price", 0)

        booking = super().create(validated_data)

        # Створити запис в історії
        BookingHistory.objects.create(
            booking=booking,
            status=booking.status,
            notes="Бронювання створено"
        )

        return booking

    def update(self, instance, validated_data):
        old_status = instance.status

        # Перерахувати ціну, якщо дати змінено
        if "start_time" in validated_data or "end_time" in validated_data:
            validated_data["total_price"] = self.context.get("total_price", instance.total_price)

        # Застосувати зміни
        booking = super().update(instance, validated_data)

        # Якщо статус змінюється, створити запис в історії
        if "status" in validated_data and old_status != booking.status:
            BookingHistory.objects.create(
                booking=booking,
                status=booking.status,
                notes=f"Статус змінено з {old_status} на {booking.status}"
            )

            # Оновити статус автомобіля, якщо бронювання стає "активним" або "завершеним"
            if booking.status == "active":
                booking.car.status = "busy"
                booking.car.save()
            elif booking.status == "completed" or booking.status == "cancelled":
                booking.car.status = "available"
                booking.car.save()

        return booking

class BookingHistorySerializer(serializers.ModelSerializer):
    """Серіалізатор для історії бронювань"""

    class Meta:
        model = BookingHistory
        fields = "__all__"
