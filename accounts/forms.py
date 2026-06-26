from django import forms
from django.contrib.auth.forms import UserChangeForm, AuthenticationForm, UserCreationForm
from django import forms

class AddCardForm(forms.Form):
    # Поля формы, но они НЕ соответствуют полям модели напрямую
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
        # Тут можно добавить простую валидацию (например, проверить длину)
        data = self.cleaned_data['card_number']
        if not data.isdigit() or len(data) < 13:
            raise forms.ValidationError("Некорректный номер карты")
        return data
class CustomAuthenticationForm(AuthenticationForm):
    """Форма входа (можно оставить как есть или добавить виджеты)"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Тут можно добавить классы Bootstrap, если нужно
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password'].widget.attrs.update({'class': 'form-control'})


class UserEditForm(UserChangeForm):
    """Форма редактирования профиля (без пароля)"""
    class Meta:
        from django.contrib.auth import get_user_model
        model = get_user_model()
        fields = ('username', 'email', 'first_name', 'last_name')  # Убрали avatar/bio, т.к. их нет у стандартного User
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'password' in self.fields:
            del self.fields['password']


class CustomUserCreationForm(UserCreationForm):
    """Форма регистрации"""
    class Meta:
        from django.contrib.auth import get_user_model
        model = get_user_model()
        fields = ('username', 'email', 'first_name', 'last_name')  
        