from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import DriverLicenseVerification, User, UserBalance


class CustomUserAdmin(UserAdmin):
    """Адмін-панель для користувачів"""

    list_display = (
        "username", "email", "first_name", "last_name",
        "is_verified_driver", "is_staff"
    )  # Поля для відображення у списку
    fieldsets = UserAdmin.fieldsets + (
        ("Додаткова інформація", {"fields": ("phone_number", "date_of_birth", "profile_picture",
                                             "driver_license_number", "driver_license_expiry",
                                             "is_verified_driver",
                                             "rating",
                                             "is_blocked")}),  # Додаткові поля для редагування
    )

class DriverLicenseVerificationAdmin(admin.ModelAdmin):
    """Адмін-панель для верифікації водійських прав"""

    list_display = ("user", "status", "created_at", "updated_at")  # Поля для відображення у списку
    list_filter = ("status",)  # Фільтри для списку
    search_fields = ("user__username", "user__email")  # Поля для пошуку
    readonly_fields = ("created_at", "updated_at")  # Поля лише для читання

class UserBalanceAdmin(admin.ModelAdmin):
    """Адмін-панель для балансу користувачів"""

    list_display = ("user", "amount")  # Поля для відображення у списку

# Реєстрація моделей у панелі адміністратора
admin.site.register(User, CustomUserAdmin)
admin.site.register(DriverLicenseVerification, DriverLicenseVerificationAdmin)
admin.site.register(UserBalance, UserBalanceAdmin)
