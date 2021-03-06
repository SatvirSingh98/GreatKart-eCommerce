import datetime
import json

from django.core.mail import EmailMessage
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string

from apps.cart.models import CartItem
from apps.orders.models import Order, OrderProduct, Payment
from apps.store.models import Product


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
    order.status = 'Accepted'
    order.save()

    # move the cart items to OrderProduct table
    cart_items = CartItem.objects.filter(user=request.user)
    for item in cart_items:
        order_product = OrderProduct()
        order_product.order_id = order.id
        order_product.payment = payment
        order_product.user_id = request.user.id
        order_product.product_id = item.product_id
        order_product.quantity = item.quantity
        order_product.product_price = item.product.price
        order_product.is_ordered = True
        order_product.save()

        # to store variations which is many-to-many field we first need to save the object.
        cart_item = CartItem.objects.get(id=item.id)
        product_variation = cart_item.variations.all()
        order_product = OrderProduct.objects.get(id=order_product.id)
        order_product.variations.set(product_variation)
        order_product.save()

        # Reduce the quantity of the sold products
        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity
        product.save()

    # Clear cart
    CartItem.objects.filter(user=request.user).delete()

    # Send order recieved email to customer
    mail_subject = 'Thank you for your order!'
    message = render_to_string('orders/order_recieved_email.html', {
        'user': request.user,
        'order': order,
    })
    to_email = order.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()

    # Send order number and transaction id back to sendData method via JsonResponse
    data = {
        'orderID': order.order_no,
        'transactionID': payment.payment_id,
    }
    return JsonResponse(data)


def order_complete_view(request):
    order_number = request.GET.get('orderID')
    transactionID = request.GET.get('paymentID')

    try:
        order = Order.objects.get(order_no=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)

        subtotal = 0
        for product in ordered_products:
            subtotal += product.product_price * product.quantity

        payment = Payment.objects.get(payment_id=transactionID)

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_no,
            'transactionID': payment.payment_id,
            'payment': payment,
            'subtotal': subtotal,
        }
        return render(request, 'orders/order_complete.html', context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('/')
