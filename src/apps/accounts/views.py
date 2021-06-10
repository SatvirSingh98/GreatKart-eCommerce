from django.shortcuts import render

from .forms import RegistrationForm


def register_view(request):
    form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    return render(request, 'accounts/login.html')
