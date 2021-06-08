from django.shortcuts import get_object_or_404, render

from apps.category.models import Category

from .models import Product


def store_view(request, category_slug=None):
    if category_slug is not None:
        category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.all().filter(category=category)
    else:
        products = Product.objects.all()
    return render(request, 'store/store.html', {'products': products})
