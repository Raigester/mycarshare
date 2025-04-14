from django.contrib import admin
from .models import CarBrand, CarModel, Car, CarPhoto, CarReview

class CarModelInline(admin.TabularInline):
    model = CarModel
    extra = 1

class CarBrandAdmin(admin.ModelAdmin):
    list_display = ('name',)
    inlines = [CarModelInline]

class CarPhotoInline(admin.TabularInline):
    model = CarPhoto
    extra = 3

class CarReviewInline(admin.TabularInline):
    model = CarReview
    extra = 0
    readonly_fields = ('user', 'rating', 'comment', 'created_at')
    can_delete = False

class CarAdmin(admin.ModelAdmin):
    list_display = ('license_plate', 'get_brand', 'get_model', 'year', 'status', 'price_per_hour', 'rating')
    list_filter = ('status', 'fuel_type', 'transmission', 'year')
    search_fields = ('license_plate', 'model__name', 'model__brand__name')
    inlines = [CarPhotoInline, CarReviewInline]
    
    def get_brand(self, obj):
        return obj.model.brand.name
    get_brand.short_description = 'Бренд'
    
    def get_model(self, obj):
        return obj.model.name
    get_model.short_description = 'Модель'

class CarModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand')
    list_filter = ('brand',)
    search_fields = ('name', 'brand__name')

class CarReviewAdmin(admin.ModelAdmin):
    list_display = ('car', 'user', 'rating', 'created_at')
    list_filter = ('rating',)
    search_fields = ('car__license_plate', 'user__username')
    readonly_fields = ('created_at',)

admin.site.register(CarBrand, CarBrandAdmin)
admin.site.register(CarModel, CarModelAdmin)
admin.site.register(Car, CarAdmin)
admin.site.register(CarReview, CarReviewAdmin)
