import datetime
import json

from django.shortcuts import redirect, render

from apps.cart.models import CartItem
from apps.orders.models import Order, Payment


def place_order_view(request, total=0, quantity=0):
    current_user = request.user
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count < 1:
        return redirect('store:store-home')

    tax, grand_total = 0, 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2 * total)/100
    grand_total = total + tax

    if request.method == 'POST':
        data = Order()
        data.user = current_user
        data.first_name = request.POST.get('first_name')
        data.last_name = request.POST.get('last_name')
        data.phone_no = request.POST.get('phone')
        data.email = request.POST.get('email')
        data.address_line_1 = request.POST.get('address_line_1')
        data.address_line_2 = request.POST.get('address_line_2')
        data.country = request.POST.get('country')
        data.state = request.POST.get('state')
        data.city = request.POST.get('city')
        data.pin_code = request.POST.get('pincode')
        data.order_note = request.POST.get('order_note')
        data.order_total = grand_total
        data.tax = tax
        data.ip = request.META.get('REMOTE_ADDR')
        data.save()

        # Generate order number
        year = int(datetime.date.today().strftime('%Y'))
        date = int(datetime.date.today().strftime('%d'))
        month = int(datetime.date.today().strftime('%m'))
        d = datetime.date(year, month, date)
        current_date = d.strftime("%Y%m%d")
        order_number = ''.join([current_date, str(data.id)])

        data.order_no = order_number
        data.save()

        order = Order.objects.get(user=current_user, is_ordered=False, order_no=order_number)
        context = {
            'order': order,
            'cart_items': cart_items,
            'total': total,
            'tax': tax,
            'grand_total': grand_total,
        }
        return render(request, 'orders/payments.html', context)
    else:
        return redirect('cart:checkout')


def payments_view(request):
    body = json.loads(request.body)
    order = Order.objects.get(user=request.user, is_ordered=False, order_no=body.get('orderID'))
    payment = Payment(
        user=request.user,
        payment_id=body.get('transactionID'),
        payment_method=body.get('payment_method'),
        status=body.get('status'),
        amount_paid=order.order_total,
    )
    payment.save()
    order.payment = payment
    order.is_ordered = True
    order.save()
    return render(request, 'orders/payments.html')
