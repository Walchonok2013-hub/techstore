
from django import forms
from django.contrib.auth.forms import UserChangeForm
from .models import User
from django.contrib.auth.forms import AuthenticationForm

from django.contrib.auth.forms import UserCreationForm




from .models import PaymentMethod

class AddCardForm(forms.ModelForm):
    class Meta:
        model = PaymentMethod
        fields = ['card_last_four', 'brand', 'expiry_month', 'expiry_year']
        widgets = {
            'card_last_four': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '****1234'}),
            'brand': forms.Select(attrs={'class': 'form-select'}),
            'expiry_month': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '12'}),
            'expiry_year': forms.NumberInput(attrs={'class': 'form-control', 'min': '2024'}),
        }

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