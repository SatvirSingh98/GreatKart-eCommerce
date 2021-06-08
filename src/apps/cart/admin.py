from django.contrib import admin

from .models import Cart, CartItem


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    '''Admin View for Cart'''

    list_display = ('cart_id', 'timestamp')


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    '''Admin View for Cart'''

    list_display = ('product', 'cart', 'quantity', 'is_active')
