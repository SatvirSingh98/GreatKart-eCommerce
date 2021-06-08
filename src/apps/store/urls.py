from django.urls import path

from .views import store_view

app_name = 'store'

urlpatterns = [
    path('', store_view, name='store-home'),
    path('<slug:category_slug>/', store_view, name='products-by-category'),
]
