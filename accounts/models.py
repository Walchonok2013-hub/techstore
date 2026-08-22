from django.db import models
from django.conf import settings
from products.models import Product
from django.contrib.auth import get_user_model
from django.db.models import Q 

User = get_user_model()

class Favorite(models.Model):
    # Теперь Django знает, кто такой User
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='user_favorites'
    )
    product = models.ForeignKey(
        'products.Product', 
        on_delete=models.CASCADE
    )
    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные товары'  
        unique_together = ('user', 'product')    

        
    def __str__(self):
        # Защита на случай, если product или user вдруг окажутся пустыми
        user_name = self.user.username if self.user else 'Unknown User'
        product_name = self.product.name if self.product else 'Unknown Product'
        return f'{user_name} - {product_name}'



class Address(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='addresses'
    )
    title = models.CharField('Название адреса', max_length=50, blank=True)
    full_address = models.TextField('Полный адрес')
    phone = models.CharField('Телефон', max_length=20)
    notes = models.TextField('Примечания для курьера', blank=True, null=True)
    is_default = models.BooleanField('Основной адрес', default=False)

    class Meta:
        verbose_name = 'Адрес доставки'
        verbose_name_plural = 'Адреса доставки'

    def __str__(self):
        return f'{self.title} ({self.full_address})'


class PaymentMethod(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payment_methods'
    )
    # ID способа оплаты в YooKassa (payment_method.id из API)
    yookassa_payment_method_id = models.CharField(
        max_length=64,
        verbose_name='ID способа оплаты в YooKassa',
        blank=True,
        null=True,
        help_text='Токен/ID способа оплаты, возвращаемый YooKassa'
    )
    # Тип способа оплаты (карта, СБП, кошелёк и т.п.) — можно брать из ответа API
    payment_type = models.CharField(
        max_length=32,
        verbose_name='Тип способа оплаты',
        blank=True,
        null=True
    )
    # Маска карты (например, "4276 00** **** 0000") — только для отображения в UI
    card_mask = models.CharField(
        max_length=32,
        verbose_name='Маска карты',
        blank=True,
        null=True,
        help_text='Отображаемая маска карты, без полных данных'
    )
    is_default = models.BooleanField(default=False, verbose_name='По умолчанию')

    class Meta:
        verbose_name = 'Способ оплаты'
        verbose_name_plural = 'Способы оплаты'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'is_default'],
                condition=Q(is_default=True),
                name='unique_default_payment_method_per_user'
            )
        ]

    def __str__(self):
        mask = self.card_mask or 'без маски'
        return f"Способ оплаты пользователя {self.user.username} ({mask})"



 
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, max_length=500, verbose_name='О себе')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Аватар')
    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'
    def __str__(self):
        return f'Профиль {self.user.username}'
    