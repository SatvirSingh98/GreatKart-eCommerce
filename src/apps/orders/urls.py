from django.urls import path

from .views import order_complete_view, payments_view, place_order_view

app_name = 'orders'

urlpatterns = [
    path('place_order/', place_order_view, name='place-order'),
    path('payments/', payments_view, name='payment'),
    path('order_complete/', order_complete_view, name='order_complete'),
]
