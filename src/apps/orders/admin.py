from django.contrib import admin

from .models import Order, OrderProduct, Payment


class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    extra = 0
    readonly_fields = ('payment', 'user', 'product', 'quantity', 'product_price', 'is_ordered', 'variation')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    '''Admin View for Payment'''

    list_display = ('__str__', 'user', 'payment_method', 'amount_paid', 'status', 'timestamp')
    ordering = ('-timestamp',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    '''Admin View for Order'''

    list_display = ('order_no', 'payment', 'full_name', 'phone_no', 'email', 'status', 'is_ordered', 'created_at')
    list_filter = ('status', 'is_ordered')
    list_per_page = 20
    search_fields = ('order_no', 'email', 'phone_no', 'first_name')
    ordering = ('-created_at',)
    inlines = [OrderProductInline]
