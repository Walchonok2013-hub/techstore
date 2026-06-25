from django import forms
from .models import Order
from accounts.models import Address

class OrderCreateForm(forms.ModelForm):
    # Добавляем поле для выбора адреса из списка адресов пользователя
    shipping_address = forms.ModelChoiceField(
        queryset=Address.objects.none(),  # Заполним в __init__
        empty_label="Выберите адрес доставки",
        label="Адрес доставки"
    )

    class Meta:
        model = Order
        fields = ['shipping_address']  # Только адрес. Остальное подтянем в views.

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Показываем только адреса текущего пользователя
            self.fields['shipping_address'].queryset = Address.objects.filter(user=user)