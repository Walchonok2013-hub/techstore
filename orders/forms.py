
from django import forms
from .models import Order 


class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'notes']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
# class OrderCreateForm(forms.ModelForm):
#     # Добавляем поле для выбора адреса из списка адресов пользователя
#     shipping_address = forms.ModelChoiceField(
#         queryset=Address.objects.none(),  # Заполним в __init__
#         empty_label="Выберите адрес доставки",
#         label="Адрес доставки"
#     )

#     class Meta:
#         model = Order
#         fields = ['shipping_address']  # Только адрес. Остальное подтянем в views.

#     def __init__(self, *args, **kwargs):
#         user = kwargs.pop('user', None)
#         super().__init__(*args, **kwargs)
        
#         if user:
#             # Показываем только адреса текущего пользователя
#             self.fields['shipping_address'].queryset = Address.objects.filter(user=user)