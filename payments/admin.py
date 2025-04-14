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
        self.message_user(request, f"Selected payments have been marked as completed")
    mark_as_completed.short_description = "Mark as completed"
    
    def mark_as_failed(self, request, queryset):
        queryset.update(status='failed')
        self.message_user(request, f"Selected payments have been marked as failed")
    mark_as_failed.short_description = "Mark as failed"
    
    def mark_as_refunded(self, request, queryset):
        queryset.update(status='refunded')
        self.message_user(request, f"Selected payments have been marked as refunded")
    mark_as_refunded.short_description = "Mark as refunded"

class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'amount', 'status', 'due_date', 'created_at')
    list_filter = ('status', 'due_date', 'created_at')
    search_fields = ('user__username', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    actions = ['mark_as_paid', 'mark_as_cancelled', 'mark_as_expired']
    
    def mark_as_paid(self, request, queryset):
        queryset.update(status='paid')
        self.message_user(request, f"Selected invoices have been marked as paid")
    mark_as_paid.short_description = "Mark as paid"
    
    def mark_as_cancelled(self, request, queryset):
        queryset.update(status='cancelled')
        self.message_user(request, f"Selected invoices have been marked as cancelled")
    mark_as_cancelled.short_description = "Mark as cancelled"
    
    def mark_as_expired(self, request, queryset):
        queryset.update(status='expired')
        self.message_user(request, f"Selected invoices have been marked as expired")
    mark_as_expired.short_description = "Mark as expired"

admin.site.register(Payment, PaymentAdmin)
admin.site.register(Invoice, InvoiceAdmin)
