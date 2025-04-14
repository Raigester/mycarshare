from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, DriverLicenseVerification

class CustomUserAdmin(UserAdmin):
    """Admin panel for users"""
    
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_verified_driver', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Information', {'fields': ('phone_number', 'date_of_birth', 'profile_picture',
                                               'driver_license_number', 'driver_license_expiry',
                                               'is_verified_driver', 'rating', 'is_blocked')}), 
    )

class DriverLicenseVerificationAdmin(admin.ModelAdmin):
    """Admin panel for driver license verification"""
    
    list_display = ('user', 'status', 'created_at', 'updated_at')
    list_filter = ('status',)
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')

admin.site.register(User, CustomUserAdmin)
admin.site.register(DriverLicenseVerification, DriverLicenseVerificationAdmin)