from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from members.models import GENDER_CHOICES, ACTIVITY_LVL_CHOICES, Profile

class CreateLoginForm(forms.Form):
    username = forms.CharField(label="Username", max_length=40)
    password = forms.CharField(label="Password", max_length=40, widget=forms.PasswordInput())

class RegisterUserForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=40)
    last_name = forms.CharField(max_length=40)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

class UpdateUserForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']


class UpdateProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('bio', 'gender', 'age', 'weight', 'height', 'activity_level')