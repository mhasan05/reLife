from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1  # Number of empty rows to show by default
    readonly_fields = ('unit_price',)  # Make unit price and total read-only

class OrderAdmin(admin.ModelAdmin):
    list_display = ('invoice_number','order_id', 'user_id', 'total_amount', 'order_status', 'order_date')
    search_fields = ('order_id', 'user_id__full_name', 'user_id__phone')
    list_filter = ('order_status', 'order_date', 'order_status')
    readonly_fields = ('invoice_number','total_amount', 'order_date', 'created_on', 'updated_on')
    inlines = [OrderItemInline]  # Display order items within the order form

    def get_total_price(self, obj):
        return obj.get_total_price()

    get_total_price.short_description = "Total Price"

admin.site.register(Order, OrderAdmin)
