from django.urls import path

from .views import (add_to_cart, cart, checkout, decrement_cart_item,
                    remove_from_cart)

app_name = 'cart'

urlpatterns = [
    path('', cart, name='cart'),
    path('add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('decrease/<int:product_id>/<int:cart_item_id>/', decrement_cart_item, name='decrement_cart_item'),
    path('remove/<int:product_id>/<int:cart_item_id>/', remove_from_cart, name='remove_from_cart'),
    path('checkout/', checkout, name='checkout'),
]
