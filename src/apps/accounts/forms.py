from django import forms
from django.contrib.auth import get_user_model

from .models import Account, UserProfile

User = get_user_model()


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

    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs_exists = User.objects.filter(email=email).exists()
        if qs_exists:
            raise forms.ValidationError('Account already exists.')
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if len(phone_number) != 10 or not phone_number.isdigit():
            raise forms.ValidationError('Please provide correct phone number!')
        return phone_number

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise forms.ValidationError('Passwords does not match!')
        return cleaned_data


class UserForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ('first_name', 'last_name', 'phone_number')

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'


class UserProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(required=False, error_messages={
                                       'invalid': ("Image files only")}, widget=forms.FileInput)

    class Meta:
        model = UserProfile
        fields = ('address_line_1', 'address_line_2', 'city', 'state', 'country', 'profile_picture', 'pin_code')

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
