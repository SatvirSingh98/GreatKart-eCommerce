from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from apps.cart.models import CartItem
from apps.cart.views import _cart_id
from apps.category.models import Category

from .models import Product


def store_view(request, category_slug=None):
    if category_slug is not None:
        category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.all().filter(category=category).order_by('id')
    else:
        products = Product.objects.all().order_by('id')

    paginator = Paginator(products, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    product_count = products.count()

    return render(request, 'store/store.html', {'products': page_obj, 'product_count': product_count})


def product_detail_view(request, category_slug=None, product_slug=None):
    product = get_object_or_404(Product, category__slug=category_slug, slug=product_slug)
    in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=product).exists()
    print(in_cart)
    return render(request, 'store/product-detail.html', {'product': product, 'in_cart': in_cart})


def search_view(request):
    query = request.GET.get('q')
    if query is not None:
        lookups = Q(name__icontains=query) | Q(slug__icontains=query)
        products = Product.objects.filter(lookups).distinct().order_by('-created_at')
        product_count = products.count()
    else:
        products = Product.objects.none()
        product_count = 0
    context = {'products': products,
               'product_count': product_count,
               'query': query}
    return render(request, 'store/store.html', context)
