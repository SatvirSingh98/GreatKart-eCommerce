from django.shortcuts import redirect, render

from apps.cart.models import Cart, CartItem
from apps.store.models import Product


def cart(request):
    return render(request, 'cart/cart.html')


def _cart_id(request):
    cart_session = request.session.session_key
    if not cart_session:
        cart_session = request.session.create()
    return cart_session


def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id)  # to get the product
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))  # get cart using cart_id present in session
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request))
    cart.save()

    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        cart_item.quantity += 1
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(product=product, cart=cart, quantity=1)
        cart_item.save()
    return redirect('cart:cart')
