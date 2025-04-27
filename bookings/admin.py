from django.contrib import admin

from .models import Booking, BookingHistory


class BookingHistoryInline(admin.TabularInline):
    model = BookingHistory
    extra = 0
    readonly_fields = ("timestamp",)  # Поля лише для читання

class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "id", "user", "car", "start_time", "end_time",
        "status", "total_price"
    )  # Поля для відображення у списку
    list_filter = ("status", "start_time", "end_time")  # Фільтри для списку
    search_fields = ("user__username", "user__email", "car__license_plate")  # Поля для пошуку
    readonly_fields = ("created_at", "updated_at")  # Поля лише для читання
    inlines = [BookingHistoryInline]  # Вбудовані моделі
    actions = [
        "mark_as_confirmed",
        "mark_as_active",
        "mark_as_completed",
        "mark_as_cancelled",
    ]  # Дії для вибраних записів

    def mark_as_confirmed(self, request, queryset):
        for booking in queryset:
            booking.status = "confirmed"  # Змінити статус на "підтверджено"
            booking.save()
            BookingHistory.objects.create(
                booking=booking,
                status="confirmed",
                notes="Статус змінено на 'Підтверджено' через панель адміністратора"
            )
        self.message_user(request, "Вибрані бронювання були позначені як підтверджені")
    mark_as_confirmed.short_description = "Позначити як підтверджені"

    def mark_as_active(self, request, queryset):
        for booking in queryset:
            booking.status = "active"  # Змінити статус на "активно"
            booking.save()
            booking.car.status = "busy"  # Змінити статус автомобіля на "зайнятий"
            booking.car.save()
            BookingHistory.objects.create(
                booking=booking,
                status="active",
                notes="Статус змінено на 'Активно' через панель адміністратора"
            )
        self.message_user(request, "Вибрані бронювання були позначені як активні")
    mark_as_active.short_description = "Позначити як активні"

    def mark_as_completed(self, request, queryset):
        for booking in queryset:
            booking.status = "completed"  # Змінити статус на "завершено"
            booking.save()
            booking.car.status = "available"  # Змінити статус автомобіля на "доступний"
            booking.car.save()
            BookingHistory.objects.create(
                booking=booking,
                status="completed",
                notes="Статус змінено на 'Завершено' через панель адміністратора"
            )
        self.message_user(request, "Вибрані бронювання були позначені як завершені")
    mark_as_completed.short_description = "Позначити як завершені"

    def mark_as_cancelled(self, request, queryset):
        for booking in queryset:
            booking.status = "cancelled"  # Змінити статус на "скасовано"
            booking.save()
            booking.car.status = "available"  # Змінити статус автомобіля на "доступний"
            booking.car.save()
            BookingHistory.objects.create(
                booking=booking,
                status="cancelled",
                notes="Статус змінено на 'Скасовано' через панель адміністратора"
            )
        self.message_user(request, "Вибрані бронювання були позначені як скасовані")
    mark_as_cancelled.short_description = "Позначити як скасовані"


admin.site.register(Booking, BookingAdmin)  # Реєстрація моделі Booking у панелі адміністратора
