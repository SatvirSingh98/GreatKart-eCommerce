from django.urls import path

from .views import (product_detail_view, search_view, store_view,
                    submit_review_view)

app_name = 'store'

urlpatterns = [
    path('', store_view, name='store-home'),
    path('category/<slug:category_slug>/', store_view, name='products-by-category'),
    path('category/<slug:category_slug>/<slug:product_slug>/', product_detail_view, name='product-detail'),
    path('search/', search_view, name='search'),
    path('submit_review/<int:product_id>/', submit_review_view, name='submit-review')
]
