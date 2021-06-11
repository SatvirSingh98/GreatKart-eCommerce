from .models import Cart, CartItem
from .views import _cart_id


def counter(request):
    cart_count = 0
    if 'admin' in request.path:
        return {}
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.all().filter(user=request.user)
        else:
            cart = Cart.objects.filter(cart_id=_cart_id(request))[:1]
            cart_items = CartItem.objects.all().filter(cart=cart)
        for cart_item in cart_items:
            cart_count += cart_item.quantity
    except Cart.DoesNotExist:
        cart_count = 0
    return {'cart_count': cart_count}
