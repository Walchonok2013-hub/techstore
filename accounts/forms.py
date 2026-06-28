from django import forms
from django.contrib.auth.forms import UserChangeForm, AuthenticationForm, UserCreationForm
from django import forms
from .models import Profile
from django.contrib.auth import get_user_model
User = get_user_model()

class UserEditForm(UserChangeForm):
    """Форма редактирования профиля (без пароля)"""
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
        # Убираем password на уровне Meta, а не через del в __init__

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # На всякий случай оставляем проверку, но при правильном Meta она не сработает
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



class CustomUserCreationForm(UserCreationForm):
    """Форма регистрации"""
    class Meta:
        from django.contrib.auth import get_user_model
        model = get_user_model()
        fields = ('username', 'email', 'first_name', 'last_name')  
        