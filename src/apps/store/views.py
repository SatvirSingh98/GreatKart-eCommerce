from django.shortcuts import get_object_or_404, render

from apps.cart.models import CartItem
from apps.cart.views import _cart_id
from apps.category.models import Category

from .models import Product


def store_view(request, category_slug=None):
    if category_slug is not None:
        category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.all().filter(category=category)
    else:
        products = Product.objects.all()
    return render(request, 'store/store.html', {'products': products})


def product_detail_view(request, category_slug=None, product_slug=None):
    product = get_object_or_404(Product, category__slug=category_slug, slug=product_slug)
    in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=product).exists()
    return render(request, 'store/product-detail.html', {'product': product, 'in_cart': in_cart})
