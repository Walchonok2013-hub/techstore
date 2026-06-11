
from django import forms
from django.contrib.auth.forms import UserChangeForm
from .models import User
from django.contrib.auth.forms import AuthenticationForm

from django.contrib.auth.forms import UserCreationForm
class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
class UserEditForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'avatar', 'bio')
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'password' in self.fields:
            del self.fields['password']
            


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User  # Указываем вашу модель
        fields = ('username', 'email', 'first_name', 'last_name', 'phone')            