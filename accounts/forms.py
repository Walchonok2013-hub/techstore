from django import forms
from django.contrib.auth.forms import UserChangeForm, AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model
from .models import Profile
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
import re
User = get_user_model()

def validate_strong_password(value):
    # Проверка длины (хотя это уже делает Django, дублирование не помешает)
    if len(value) < 12:
        raise ValidationError("Пароль должен быть не менее 12 символов.")
    
    # Проверка на наличие заглавной буквы
    if not re.search(r'[A-Z]', value):
        raise ValidationError("Пароль должен содержать хотя бы одну заглавную букву (A-Z).")
    
    # Проверка на наличие строчной буквы
    if not re.search(r'[a-z]', value):
        raise ValidationError("Пароль должен содержать хотя бы одну строчную букву (a-z).")
    
    # Проверка на наличие цифры
    if not re.search(r'\d', value):
        raise ValidationError("Пароль должен содержать хотя бы одну цифру (0-9).")
    
    # Проверка на наличие спецсимвола
    # Ищем любой символ, который НЕ является буквой и НЕ является цифрой
    if not re.search(r'[^A-Za-z0-9]', value):
        raise ValidationError(r"Пароль должен содержать хотя бы один специальный символ (!, @, #, $ и т.д.).")

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email')

    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'first_name', 'last_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        
        self.fields['username'].help_text = '' 
        # Или можно использовать: self.fields['username'].help_text = None
        
      
        self.fields['password1'].help_text = "Минимум 12 символов, заглавная буква, цифра и спецсимвол."
        self.fields['password2'].help_text = "Повторите тот же пароль."

       
        self.fields['first_name'].label = 'Имя'
        self.fields['last_name'].label = 'Фамилия'
        
        
        self.fields['password1'].validators.append(validate_strong_password)




class UserEditForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'password' in self.fields:
            del self.fields['password']


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('avatar', 'bio')
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }


class AddCardForm(forms.Form):
    card_number = forms.CharField(
        max_length=20,
        label='Номер карты',
        widget=forms.TextInput(attrs={'placeholder': '1234 5678 9012 3456'})
    )
    expiry_month = forms.IntegerField(
        label='Месяц (MM)',
        min_value=1,
        max_value=12
    )
    expiry_year = forms.IntegerField(
        label='Год (YY)',
        min_value=24,
        max_value=34
    )
    cvv = forms.CharField(
        max_length=4,
        label='CVV/CVC',
        widget=forms.PasswordInput()
    )

    def clean_card_number(self):
        data = self.cleaned_data['card_number']
        cleaned = data.replace(' ', '')
        if not cleaned.isdigit() or len(cleaned) < 13:
            raise forms.ValidationError("Некорректный номер карты")
        return cleaned


class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password'].widget.attrs.update({'class': 'form-control'})



        