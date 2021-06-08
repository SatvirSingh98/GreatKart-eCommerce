from django.urls import path

from .views import product_detail_view, store_view

app_name = 'store'

urlpatterns = [
    path('', store_view, name='store-home'),
    path('<slug:category_slug>/', store_view, name='products-by-category'),
    path('<slug:category_slug>/<slug:product_slug>/', product_detail_view, name='product-detail'),
]
