from django import forms

from .models import Account


class RegistrationForm(forms.ModelForm):
    """Form definition for Registration."""

    class Meta:
        """Meta definition for Registrationform."""

        model = Account
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'password',)
