from django.urls import path

from .views import add_to_cart, cart

app_name = 'cart'

urlpatterns = [
    path('', cart, name='cart'),
    path('add/<int:product_id>/', add_to_cart, name='add_to_cart'),
]
