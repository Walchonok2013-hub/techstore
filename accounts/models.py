from django.db import models
from django.conf import settings
from products.models import Product

from django.db import models
from django.contrib.auth import get_user_model

# Эта строка создает переменную User, которую мы будем использовать в ForeignKey
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
    # ВНИМАНИЕ: Никогда не храните реальные номера карт в открытом виде в БД!
    # Для примера оставляем, но в продакшене используйте токенизацию (Stripe, YooKassa и т.д.)
    card_number = models.CharField(max_length=20, verbose_name='Номер карты')
    is_default = models.BooleanField(default=False, verbose_name='По умолчанию')

    class Meta:
        verbose_name = 'Способ оплаты'
        verbose_name_plural = 'Способы оплаты'

    def __str__(self):
        return f"Карта пользователя {self.user.username}"
 
