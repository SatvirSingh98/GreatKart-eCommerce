from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.http.response import HttpResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import (is_safe_url, urlsafe_base64_decode,
                               urlsafe_base64_encode)

from .forms import RegistrationForm

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

        current_site = get_current_site(request)
        mail_subject = 'Please activate your account...'
        message = render_to_string('accounts/verification_email.html', {
            'user': user,
            'domain': current_site,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': default_token_generator.make_token(user),
        })
        to_email = email
        send_email = EmailMessage(mail_subject, message, to=[to_email])
        send_email.send()
        return redirect(f'/accounts/login/?activation=verification&email={email}')

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        # for redirecting after login
        next_ = request.GET.get('next')
        next_post = request.POST.get('next')
        redirect_path = next_ or next_post

        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(email=email, password=password)
        if user is not None:
            login(request, user)
            first_name = request.user.first_name.title()
            last_name = request.user.last_name.title()
            if is_safe_url(redirect_path, request.get_host()):
                messages.success(request, f"Welcome {first_name} {last_name}")
                path = redirect_path.split('=')[1]
                return redirect(path)
            else:
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
        messages.success(request, 'Congractulations! Your account is activated.')
        return redirect('accounts:login')
    else:
        messages.error(request, 'Invalid activation link.')
        return redirect('accounts:register')


@login_required(login_url='accounts:login')
def dashboard_view(request):
    return render(request, 'accounts/dashboard.html')


def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email__iexact=email.lower())

            current_site = get_current_site(request)
            mail_subject = 'Reset your password.'
            message = render_to_string('accounts/reset_password.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            messages.success(request, 'Password reset email has been sent to your email address.')
        else:
            messages.error(request, 'Account does not exist!')
    return render(request, 'accounts/forgot_password.html')


def reset_password_validate_view(request, uidb64, token):
    return HttpResponse('Code Success...')
