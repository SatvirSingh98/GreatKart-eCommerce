from django.contrib.auth import get_user_model
from django.contrib import messages
from django.shortcuts import redirect, render

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
        messages.success(request, 'Registration Successfull')
        return redirect('accounts:login')

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    return render(request, 'accounts/login.html')
