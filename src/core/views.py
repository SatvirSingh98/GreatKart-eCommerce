from django.shortcuts import render

from apps.store.models import Product


def index(request):
    products = Product.objects.all().order_by('created_at')
    context = {
        'stars': [0.5, 1.5, 2.5, 3.5, 4.5],
        'products': products
    }
    return render(request, 'index.html', context)
