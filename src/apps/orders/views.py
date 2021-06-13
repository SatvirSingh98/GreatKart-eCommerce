from django.shortcuts import redirect

from apps.cart.models import CartItem
from apps.orders.models import Order


def place_order_view(request):
    cart_count = CartItem.objects.filter(user=request.user).count()
    if cart_count < 1:
        return redirect('store:store-home')

    if request.method == 'POST':
        data = Order()
        data.first_name = request.POST.get('first_name')
        data.last_name = request.POST.get('last_name')
        data.phone_no = request.POST.get('phone')
        data.email = request.POST.get('email')
        data.address_line_1 = request.POST.get('address_line_1')
        data.address_line_2 = request.POST.get('address_line_2')
        data.country = request.POST.get('country')
        data.state = request.POST.get('state')
        data.city = request.POST.get('city')
        data.pin_code = request.POST.get('pin_code')
        data.order_note = request.POST.get('order_note')

    return redirect('cart:checkout')
