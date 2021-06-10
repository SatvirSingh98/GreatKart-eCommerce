from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

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
        messages.success(request, 'Registration Successfull')
        return redirect('accounts:login')

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(email=email, password=password)
        if user is not None:
            login(request, user)
            first_name = request.user.first_name.title()
            last_name = request.user.last_name.title()
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
