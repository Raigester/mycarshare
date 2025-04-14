from django.contrib import admin
from .models import Payment, Invoice

class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'amount', 'payment_type', 'status', 'created_at')
    list_filter = ('status', 'payment_type', 'created_at')
    search_fields = ('user__username', 'transaction_id', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    actions = ['mark_as_completed', 'mark_as_failed', 'mark_as_refunded']
    
    def mark_as_completed(self, request, queryset):
        queryset.update(status='completed')
        self.message_user(request, f"Выбранные платежи отмечены как завершенные")
    mark_as_completed.short_description = "Отметить как завершенные"
    
    def mark_as_failed(self, request, queryset):
        queryset.update(status='failed')
        self.message_user(request, f"Выбранные платежи отмечены как неудачные")
    mark_as_failed.short_description = "Отметить как неудачные"
    
    def mark_as_refunded(self, request, queryset):
        queryset.update(status='refunded')
        self.message_user(request, f"Выбранные платежи отмечены как возвращенные")
    mark_as_refunded.short_description = "Отметить как возвращенные"

class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'amount', 'status', 'due_date', 'created_at')
    list_filter = ('status', 'due_date', 'created_at')
    search_fields = ('user__username', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    actions = ['mark_as_paid', 'mark_as_cancelled', 'mark_as_expired']
    
    def mark_as_paid(self, request, queryset):
        queryset.update(status='paid')
        self.message_user(request, f"Выбранные счета отмечены как оплаченные")
    mark_as_paid.short_description = "Отметить как оплаченные"
    
    def mark_as_cancelled(self, request, queryset):
        queryset.update(status='cancelled')
        self.message_user(request, f"Выбранные счета отмечены как отмененные")
    mark_as_cancelled.short_description = "Отметить как отмененные"
    
    def mark_as_expired(self, request, queryset):
        queryset.update(status='expired')
        self.message_user(request, f"Выбранные счета отмечены как истекшие")
    mark_as_expired.short_description = "Отметить как истекшие"

admin.site.register(Payment, PaymentAdmin)
admin.site.register(Invoice, InvoiceAdmin)
