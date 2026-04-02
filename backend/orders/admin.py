from django.contrib import admin
from .models import Order, OrderItem, OrderStatusHistory

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'business', 'status', 'total', 'created_at']
    list_filter = ['status', 'created_at', 'business']
    search_fields = ['customer__username', 'business__name', 'tracking_number']
    readonly_fields = ['created_at', 'updated_at', 'delivered_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Order Information', {
            'fields': ('customer', 'business', 'status', 'tracking_number')
        }),
        ('Pricing', {
            'fields': ('subtotal', 'delivery_fee', 'tax', 'total')
        }),
        ('Delivery', {
            'fields': ('delivery_address', 'delivery_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'delivered_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity', 'price', 'total_price']
    list_filter = ['order__status', 'order__created_at']
    search_fields = ['product__name', 'order__id']
    readonly_fields = ['total_price']
    
    def total_price(self, obj):
        return obj.total_price
    total_price.short_description = 'Total Price'

@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['order', 'status', 'updated_by', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order__id', 'updated_by__username']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
