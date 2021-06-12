from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404, redirect, render

from apps.cart.models import Cart, CartItem
from apps.store.models import Product, Variation


def cart(request, total=0, quantity=0, cart_items=None):
    tax, grand_total = 0, 0
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += cart_item.product.price * cart_item.quantity
            quantity += cart_item.quantity
    except ObjectDoesNotExist:
        pass
    tax = (18 * total)/100
    grand_total = total + tax
    context = {'total': total, 'quantity': quantity, 'cart_items': cart_items,
               'tax': tax, 'grand_total': grand_total}
    return render(request, 'cart/cart.html', context)


def _cart_id(request):
    cart_session = request.session.session_key
    if not cart_session:
        cart_session = request.session.create()
    return cart_session


def add_to_cart(request, product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id)  # to get the product

    product_variation = []
    if request.method == 'POST':
        for item in request.POST:
            key = item
            value = request.POST.get(item)
            try:
                variation = Variation.objects.get(product=product, variation_category__iexact=key,
                                                  variation_value__iexact=value)
                product_variation.append(variation)
            except Exception:
                pass

    if current_user.is_authenticated:
        cart_item = CartItem.objects.filter(product=product, user=current_user)
        if cart_item.exists():
            existing_variation_list = []
            ids = []
            for item in cart_item:
                variations = item.variations.all()
                existing_variation_list.append(list(variations))
                ids.append(item.id)

            if product_variation in existing_variation_list:
                index = existing_variation_list.index(product_variation)
                item_id = ids[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()
            else:
                item = CartItem.objects.create(product=product, user=current_user, quantity=1)
                if len(product_variation) > 0:
                    item.variations.add(*product_variation)
                item.save()
        else:
            cart_item = CartItem.objects.create(product=product, user=current_user, quantity=1)
            if len(product_variation) > 0:
                cart_item.variations.add(*product_variation)
            cart_item.save()
    else:
        cart, _ = Cart.objects.get_or_create(cart_id=_cart_id(request))  # get cart using cart_id present in session
        cart_item = CartItem.objects.filter(product=product, cart=cart)
        if cart_item.exists():
            existing_variation_list = []
            ids = []
            for item in cart_item:
                variations = item.variations.all()
                existing_variation_list.append(list(variations))
                ids.append(item.id)

            if product_variation in existing_variation_list:
                index = existing_variation_list.index(product_variation)
                item_id = ids[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()
            else:
                item = CartItem.objects.create(product=product, cart=cart, quantity=1)
                if len(product_variation) > 0:
                    item.variations.add(*product_variation)
                item.save()
        else:
            cart_item = CartItem.objects.create(product=product, cart=cart, quantity=1)
            if len(product_variation) > 0:
                cart_item.variations.add(*product_variation)
            cart_item.save()
    return redirect('cart:cart')


def decrement_cart_item(request, product_id, cart_item_id):
    user = request.user
    product = get_object_or_404(Product, id=product_id)
    if user.is_authenticated:
        cart_item = CartItem.objects.get(product=product, user=user, id=cart_item_id)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart:cart')


def remove_from_cart(request, product_id, cart_item_id):
    user = request.user
    product = get_object_or_404(Product, id=product_id)
    if user.is_authenticated:
        CartItem.objects.get(product=product, user=user, id=cart_item_id).delete()
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        CartItem.objects.get(product=product, cart=cart, id=cart_item_id).delete()
    return redirect('cart:cart')


@login_required(login_url='accounts:login')
def checkout(request, total=0, quantity=0, cart_items=None):
    tax, grand_total = 0, 0
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += cart_item.product.price * cart_item.quantity
            quantity += cart_item.quantity
    except ObjectDoesNotExist:
        pass
    tax = (18 * total)/100
    grand_total = total + tax
    context = {'total': total, 'quantity': quantity, 'cart_items': cart_items,
               'tax': tax, 'grand_total': grand_total}
    return render(request, 'store/checkout.html', context)
