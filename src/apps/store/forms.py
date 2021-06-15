from django import forms

from .models import ReviewModel


class ReviewModelForm(forms.ModelForm):
    class Meta:
        model = ReviewModel
        fields = ('review', 'rating')
