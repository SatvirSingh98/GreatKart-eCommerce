from django.urls import path

from .views import place_order_view

app_name = 'orders'

urlpatterns = [
    path('place_order/', place_order_view, name='place-order'),
]
