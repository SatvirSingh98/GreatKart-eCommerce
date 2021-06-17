from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.cart.models import CartItem
from apps.cart.views import _cart_id
from apps.category.models import Category
from apps.orders.models import OrderProduct

from .forms import ReviewModelForm
from .models import Product, ReviewModel


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

    if request.user.is_authenticated:
        try:
            order_product_exists = OrderProduct.objects.filter(user=request.user, product_id=product.id).exists()
        except OrderProduct.DoesNotExist:
            order_product_exists = None
    else:
        order_product_exists = None

    # Get the reviews
    reviews = ReviewModel.objects.filter(product_id=product.id, status=True).order_by('-created_at')

    context = {
        'product': product,
        'in_cart': in_cart,
        'order_product_exists': order_product_exists,
        'reviews': reviews,
        'stars': [0.5, 1.5, 2.5, 3.5, 4.5],
    }
    return render(request, 'store/product-detail.html', context)


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


@login_required(login_url='accounts:login')
def submit_review_view(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            reviews = ReviewModel.objects.get(user_id=request.user.id, product_id=product_id)
            form = ReviewModelForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Thank you! Your review has been updated.')
            return redirect(url)
        except ReviewModel.DoesNotExist:
            form = ReviewModelForm(request.POST)
            if form.is_valid():
                data = ReviewModel()
                data.rating = form.cleaned_data.get('rating')
                data.review = form.cleaned_data.get('review')
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
            messages.success(request, 'Thank you! Your review has been submitted.')
            return redirect(url)
