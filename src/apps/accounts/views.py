import requests
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from apps.cart.models import Cart, CartItem
from apps.cart.views import _cart_id
from apps.orders.models import Order, OrderProduct
from core.utils import render_to_pdf

from .forms import RegistrationForm, UserForm, UserProfileForm
from .models import UserProfile

User = get_user_model()


def register_view(request):
    form = RegistrationForm(request.POST or None)
    if form.is_valid():
        first_name = form.cleaned_data.get('first_name')
        last_name = form.cleaned_data.get('last_name')
        email = form.cleaned_data.get('email')
        phone_number = form.cleaned_data.get('phone_number')
        password = form.cleaned_data.get('password')
        username = email.split('@')[0]

        user = User.objects.create_user(first_name=first_name, last_name=last_name,
                                        username=username, email=email, password=password)
        user.phone_number = phone_number
        user.save()

        # create user profile
        profile = UserProfile()
        profile.user_id = user.id
        profile.profile_picture = 'default/avatar.png'
        profile.save()

        current_site = get_current_site(request)
        mail_subject = 'Please activate your account...'
        message = render_to_string('accounts/verification_email.html', {
            'user': user,
            'domain': current_site,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': default_token_generator.make_token(user),
            'secure': request.is_secure()
        })
        to_email = email
        send_email = EmailMessage(mail_subject, message, to=[to_email])
        send_email.send()
        return redirect(f'/accounts/login/?activation=verification&email={email}')

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(email=email, password=password)
        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                cart_item = CartItem.objects.filter(cart=cart)

                if cart_item.exists():
                    # Getting the product variations by cart_id
                    product_variation = []
                    for item in cart_item:
                        variations = item.variations.all()
                        product_variation.append(list(variations))

                    # Getting the cart items from the user to access his product variations
                    cart_item = CartItem.objects.filter(user=user)
                    existing_variation_list = []
                    ids = []
                    for item in cart_item:
                        variations = item.variations.all()
                        existing_variation_list.append(list(variations))
                        ids.append(item.id)

                    for pr_var in product_variation:
                        if pr_var in existing_variation_list:
                            index = existing_variation_list.index(pr_var)
                            item_id = ids[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user = user
                                item.save()
            except Exception:
                pass

            login(request, user)
            first_name = request.user.first_name.title()
            last_name = request.user.last_name.title()
            try:
                HTTP_REFERER = request.META.get('HTTP_REFERER')
                path = requests.utils.urlparse(HTTP_REFERER).query
                redirect_path = dict(x.split('=') for x in path.split('&'))
                messages.success(request, f"Welcome {first_name} {last_name}")
                return redirect(redirect_path.get('next'))
            except Exception:
                messages.success(request, f"Welcome {first_name} {last_name}")
                return redirect('/')
        else:
            messages.error(request, 'Invalid Credentials!')
    return render(request, 'accounts/login.html')


@login_required(login_url='accounts:login')
def logout_view(request):
    logout(request)
    messages.info(request, 'You are successfully logged out!!!')
    return redirect('/')


def activate_email_view(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations! Your account is activated.')
        return redirect('accounts:login')
    else:
        messages.error(request, 'Invalid activation link.')
        return redirect('accounts:register')


@login_required(login_url='accounts:login')
def dashboard_view(request):
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id, is_ordered=True)
    orders_count = orders.count()
    userprofile = UserProfile.objects.get(user_id=request.user.id)
    context = {
        'orders_count': orders_count,
        'userprofile': userprofile,
    }
    return render(request, 'accounts/dashboard.html', context)


def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email__iexact=email.lower())

            current_site = get_current_site(request)
            mail_subject = 'Reset your password.'
            message = render_to_string('accounts/verification_reset_password.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            return redirect(f'/accounts/reset-password/?activation=verification&email={email}')
        else:
            messages.error(request, 'Account does not exist!')
    return render(request, 'accounts/forgot_password.html')


def reset_password_validate_view(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password.')
        return redirect('accounts:reset-password')
    else:
        messages.error(request, 'Invalid activation link.')
        return redirect('accounts:register')


def reset_password_view(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password == confirm_password:
            user = User.objects.get(id=request.session.get('uid'))
            user.set_password(password)
            user.save()
            messages.success(request, 'Your password has been reset successfully.')
            return redirect('accounts:login')
        else:
            messages.error(request, 'Passwords does not match!')
    return render(request, 'accounts/reset_password.html')


@login_required(login_url='login')
def my_orders_view(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    context = {
        'orders': orders,
    }
    return render(request, 'accounts/my_orders.html', context)


@login_required(login_url='accounts:login')
def edit_profile_view(request):
    user = request.user
    userprofile = get_object_or_404(UserProfile, user=user)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('accounts:edit-profile')
    else:
        user_form = UserForm(instance=user)
        profile_form = UserProfileForm(instance=userprofile)
    context = {
        'user': user,
        'user_form': user_form,
        'profile_form': profile_form,
        'userprofile': userprofile,
    }
    return render(request, 'accounts/edit_profile.html', context)


@login_required(login_url='accounts:login')
def remove_profile_picture_view(request):
    userprofile = get_object_or_404(UserProfile, user=request.user)
    if userprofile.profile_picture is not None:
        userprofile.profile_picture.delete(save=False)
        userprofile.profile_picture = 'default/avatar.png'
        userprofile.save()
        messages.success(request, 'Profile picture successfully removed.')
    return redirect('accounts:edit-profile')


@login_required(login_url='accounts:login')
def change_password_view(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        user = User.objects.get(username__exact=request.user.username)

        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Password updated successfully.')
                return redirect('accounts:dashboard')
            else:
                messages.error(request, 'Please enter valid current password.')
                return redirect('accounts:change-password')
        else:
            messages.error(request, 'Password does not match!')
            return redirect('accounts:change-password')
    return render(request, 'accounts/change_password.html')


@login_required(login_url='accounts:login')
def change_email_view(request):
    if request.method == 'POST':
        current_email = request.POST.get('current_email').lower()
        new_email = request.POST.get('new_email').lower()
        confirm_email = request.POST.get('confirm_email').lower()
        username = new_email.split('@')[0]

        user = User.objects.get(username__exact=request.user.username)

        if new_email == confirm_email:
            if user.email == current_email:
                user.email = new_email
                user.username = username
                user.save()
                logout(request)
                messages.success(request, 'Email updated successfully.')
                return redirect('accounts:dashboard')
            else:
                messages.error(request, 'This email is not registered with the current user.')
                return redirect('accounts:change-email')
        else:
            messages.error(request, 'Email does not match!')
            return redirect('accounts:change-email')
    return render(request, 'accounts/change_email.html')


@login_required(login_url='accounts:login')
def order_detail_view(request, order_no):
    order_detail = OrderProduct.objects.filter(order__order_no=order_no)
    order = Order.objects.get(order_no=order_no)
    subtotal = 0
    for i in order_detail:
        subtotal += i.product_price * i.quantity

    context = {
        'order_detail': order_detail,
        'order': order,
        'subtotal': subtotal,
    }
    return render(request, 'accounts/order_detail.html', context)


@login_required(login_url='accounts:login')
def print_to_pdf_view(request, order_no):
    order_detail = OrderProduct.objects.filter(order__order_no=order_no)
    order = Order.objects.get(order_no=order_no)
    subtotal = 0
    for i in order_detail:
        subtotal += i.product_price * i.quantity

    context = {
        'order_detail': order_detail,
        'order': order,
        'subtotal': subtotal,
    }
    return render_to_pdf(request, template_path='accounts/snippets/invoice.html', data=context, filename=order_no)
