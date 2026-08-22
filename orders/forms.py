import re
from django import forms
from .models import Order

class OrderCreateForm(forms.ModelForm):
    
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'notes']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Иван'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Иванов'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ivan@example.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+7 (999) 000-00-00'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Город, улица, дом'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Подъезд, этаж, код домофона...'}),
        }

    def clean_first_name(self):
        value = self.cleaned_data.get('first_name', '').strip()
        print(f"--- DEBUG: Проверяем имя: '{value}' (тип: {type(value)}) ---")

        if not value:
            raise forms.ValidationError('Это поле обязательно для заполнения.')

        pattern = r'^[а-яА-ЯёЁa-zA-Z\s-]+$'
        if not re.match(pattern, value):
            print("--- DEBUG: ОШИБКА ВАЛИДАЦИИ! ---")
            raise forms.ValidationError('Имя должно содержать только буквы, пробелы и дефисы.')

        print("--- DEBUG: Имя валидно ---")
        return value

    def clean_last_name(self):
        value = self.cleaned_data.get('last_name', '').strip()
        if not value:
            raise forms.ValidationError('Это поле обязательно для заполнения.')
        if len(value) < 2 or len(value) > 50:
            raise forms.ValidationError('Фамилия должна быть от 2 до 50 символов.')
        if not re.match(r'^[а-яА-ЯёЁa-zA-Z\s-]+$', value):
            raise forms.ValidationError('Фамилия должна содержать только буквы, пробелы и дефисы.')
        return value

    def clean_email(self):
        value = self.cleaned_data.get('email', '').strip()
        if not value:
            raise forms.ValidationError('Email обязателен.')

        # Django уже проверяет формат, можно оставить дополнительную проверку
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, value):
            raise forms.ValidationError('Пожалуйста, введите корректный адрес электронной почты.')
        return value

    def clean_address(self):
        value = self.cleaned_data.get('address', '').strip()
        if not value:
            raise forms.ValidationError('Адрес доставки обязателен.')

        if not re.match(r'^[а-яА-ЯёЁa-zA-Z0-9\s,/().]+$', value):
            raise forms.ValidationError('Адрес содержит недопустимые символы.')

        if re.fullmatch(r'\d+', value):
            raise forms.ValidationError('Адрес не может состоять только из цифр.')

        return value
    
    def clean_phone(self):
        value = self.cleaned_data.get('phone', '').strip()
        
        # Оставляем только цифры
        digits_only = re.sub(r'\D', '', value)
        
        if not digits_only:
            raise forms.ValidationError('Пожалуйста, введите корректный номер телефона (только цифры).')
        
        # Опционально: проверка длины (например, от 10 до 15 цифр)
        if len(digits_only) < 10 or len(digits_only) > 15:
            raise forms.ValidationError('Номер телефона должен содержать от 10 до 15 цифр.')
            
        return value 