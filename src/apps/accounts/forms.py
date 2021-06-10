from django import forms

from .models import Account


class RegistrationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields.get('first_name').widget.attrs['placeholder'] = 'first name'
        self.fields.get('last_name').widget.attrs['placeholder'] = 'last name'
        self.fields.get('email').widget.attrs['placeholder'] = 'provide working email id'
        self.fields.get('phone_number').widget.attrs['placeholder'] = 'phone number'
        for field in self.fields:
            self.fields.get(field).widget.attrs['class'] = 'form-control'

    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Enter Password',
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Confirm Password',
    }))

    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'password']
