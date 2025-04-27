from django.contrib import admin

from .models import Car, CarBrand, CarModel, CarPhoto, CarReview


class CarModelInline(admin.TabularInline):
    """Вбудована модель для відображення моделей автомобілів у бренді"""
    model = CarModel
    extra = 1  # Кількість порожніх рядків для додавання нових записів

class CarBrandAdmin(admin.ModelAdmin):
    """Адмін-панель для брендів автомобілів"""
    list_display = ("name",)  # Поля для відображення у списку
    inlines = [CarModelInline]  # Вбудована модель для моделей автомобілів

class CarPhotoInline(admin.TabularInline):
    """Вбудована модель для відображення фотографій автомобілів"""
    model = CarPhoto
    extra = 3  # Кількість порожніх рядків для додавання нових записів

class CarReviewInline(admin.TabularInline):
    """Вбудована модель для відображення відгуків про автомобілі"""
    model = CarReview
    extra = 0  # Не додавати порожні рядки для нових записів
    readonly_fields = ("user", "rating", "comment", "created_at")  # Поля лише для читання
    can_delete = False  # Заборонити видалення відгуків

class CarAdmin(admin.ModelAdmin):
    """Адмін-панель для автомобілів"""
    list_display = (
        "license_plate", "get_brand", "get_model",
        "year", "status", "rating"
    )  # Поля для відображення у списку
    list_filter = ("status", "fuel_type", "transmission", "year")  # Фільтри для списку
    search_fields = ("license_plate", "model__name", "model__brand__name")  # Поля для пошуку
    inlines = [CarPhotoInline, CarReviewInline]  # Вбудовані моделі для фотографій та відгуків

    def get_brand(self, obj):
        """Отримати назву бренду автомобіля"""
        return obj.model.brand.name
    get_brand.short_description = "Бренд"  # Назва колонки у списку

    def get_model(self, obj):
        """Отримати назву моделі автомобіля"""
        return obj.model.name
    get_model.short_description = "Модель"  # Назва колонки у списку

class CarModelAdmin(admin.ModelAdmin):
    """Адмін-панель для моделей автомобілів"""
    list_display = ("name", "brand")  # Поля для відображення у списку
    list_filter = ("brand",)  # Фільтри для списку
    search_fields = ("name", "brand__name")  # Поля для пошуку

class CarReviewAdmin(admin.ModelAdmin):
    """Адмін-панель для відгуків про автомобілі"""
    list_display = ("car", "user", "rating", "created_at")  # Поля для відображення у списку
    list_filter = ("rating",)  # Фільтри для списку
    search_fields = ("car__license_plate", "user__username")  # Поля для пошуку
    readonly_fields = ("created_at",)  # Поля лише для читання

# Реєстрація моделей у панелі адміністратора
admin.site.register(CarBrand, CarBrandAdmin)
admin.site.register(CarModel, CarModelAdmin)
admin.site.register(Car, CarAdmin)
admin.site.register(CarReview, CarReviewAdmin)
