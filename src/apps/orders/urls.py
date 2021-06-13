from django.urls import path

from .views import payments_view, place_order_view

app_name = 'orders'

urlpatterns = [
    path('place_order/', place_order_view, name='place-order'),
    path('payments/', payments_view, name='payment')
]
