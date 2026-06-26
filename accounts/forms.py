from django import forms
from django.contrib.auth.forms import UserChangeForm, AuthenticationForm, UserCreationForm

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
        