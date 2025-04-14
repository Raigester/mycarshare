from django.contrib import admin
from .models import Booking, BookingHistory

class BookingHistoryInline(admin.TabularInline):
    model = BookingHistory
    extra = 0
    readonly_fields = ('timestamp',)

class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'car', 'start_time', 'end_time', 'status', 'total_price')
    list_filter = ('status', 'start_time', 'end_time')
    search_fields = ('user__username', 'user__email', 'car__license_plate')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [BookingHistoryInline]
    actions = ['mark_as_confirmed', 'mark_as_active', 'mark_as_completed', 'mark_as_cancelled']
    
    def mark_as_confirmed(self, request, queryset):
        for booking in queryset:
            booking.status = 'confirmed'
            booking.save()
            BookingHistory.objects.create(
                booking=booking,
                status='confirmed',
                notes="Статус изменен на 'Подтверждено' через административную панель"
            )
        self.message_user(request, f"Выбранные бронирования отмечены как подтвержденные")
    mark_as_confirmed.short_description = "Отметить как подтвержденные"
    
    def mark_as_active(self, request, queryset):
        for booking in queryset:
            booking.status = 'active'
            booking.save()
            booking.car.status = 'busy'
            booking.car.save()
            BookingHistory.objects.create(
                booking=booking,
                status='active',
                notes="Статус изменен на 'Активно' через административную панель"
            )
        self.message_user(request, f"Выбранные бронирования отмечены как активные")
    mark_as_active.short_description = "Отметить как активные"
    
    def mark_as_completed(self, request, queryset):
        for booking in queryset:
            booking.status = 'completed'
            booking.save()
            booking.car.status = 'available'
            booking.car.save()
            BookingHistory.objects.create(
                booking=booking,
                status='completed',
                notes="Статус изменен на 'Завершено' через административную панель"
            )
        self.message_user(request, f"Выбранные бронирования отмечены как завершенные")
    mark_as_completed.short_description = "Отметить как завершенные"
    
    def mark_as_cancelled(self, request, queryset):
        for booking in queryset:
            booking.status = 'cancelled'
            booking.save()
            booking.car.status = 'available'
            booking.car.save()
            BookingHistory.objects.create(
                booking=booking,
                status='cancelled',
                notes="Статус изменен на 'Отменено' через административную панель"
            )
        self.message_user(request, f"Выбранные бронирования отмечены как отмененные")
    mark_as_cancelled.short_description = "Отметить как отмененные"

class BookingHistoryAdmin(admin.ModelAdmin):
    list_display = ('booking', 'status', 'timestamp')
    list_filter = ('status', 'timestamp')
    search_fields = ('booking__user__username', 'booking__car__license_plate', 'notes')
    readonly_fields = ('timestamp',)

admin.site.register(Booking, BookingAdmin)
admin.site.register(BookingHistory, BookingHistoryAdmin)
