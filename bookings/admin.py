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
                notes="Status changed to 'Confirmed' via admin panel"
            )
        self.message_user(request, f"Selected bookings have been marked as confirmed")
    mark_as_confirmed.short_description = "Mark as confirmed"
    
    def mark_as_active(self, request, queryset):
        for booking in queryset:
            booking.status = 'active'
            booking.save()
            booking.car.status = 'busy'
            booking.car.save()
            BookingHistory.objects.create(
                booking=booking,
                status='active',
                notes="Status changed to 'Active' via admin panel"
            )
        self.message_user(request, f"Selected bookings have been marked as active")
    mark_as_active.short_description = "Mark as active"
    
    def mark_as_completed(self, request, queryset):
        for booking in queryset:
            booking.status = 'completed'
            booking.save()
            booking.car.status = 'available'
            booking.car.save()
            BookingHistory.objects.create(
                booking=booking,
                status='completed',
                notes="Status changed to 'Completed' via admin panel"
            )
        self.message_user(request, f"Selected bookings have been marked as completed")
    mark_as_completed.short_description = "Mark as completed"
    
    def mark_as_cancelled(self, request, queryset):
        for booking in queryset:
            booking.status = 'cancelled'
            booking.save()
            booking.car.status = 'available'
            booking.car.save()
            BookingHistory.objects.create(
                booking=booking,
                status='cancelled',
                notes="Status changed to 'Cancelled' via admin panel"
            )
        self.message_user(request, f"Selected bookings have been marked as cancelled")
    mark_as_cancelled.short_description = "Mark as cancelled"

class BookingHistoryAdmin(admin.ModelAdmin):
    list_display = ('booking', 'status', 'timestamp')
    list_filter = ('status', 'timestamp')
    search_fields = ('booking__user__username', 'booking__car__license_plate', 'notes')
    readonly_fields = ('timestamp',)

admin.site.register(Booking, BookingAdmin)
admin.site.register(BookingHistory, BookingHistoryAdmin)
