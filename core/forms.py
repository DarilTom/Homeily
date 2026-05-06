from django import forms
from django.contrib.auth.models import User
from .models import UserProfile

# Form for the built-in Django User model
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'email']

# Form for our custom UserProfile model
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone', 'address']