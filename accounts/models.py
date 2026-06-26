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
    title = models.CharField(max_length=100, default='Основной адрес')
    full_address = models.TextField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Адрес'
        verbose_name_plural = 'Адреса'

    def __str__(self):
        return f"{self.title} ({self.full_address})"



# from django.db import models
# from django.conf import settings
# from products.models import Product

# from django.dispatch import receiver

# # Используем строковую ссылку для ForeignKey - это стандарт Django
# # Не используем get_user_model() на уровне модуля для полей моделей

# class Favorite(models.Model):
#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL, 
#         on_delete=models.CASCADE, 
#         related_name='user_favorites'
#     )
#     product = models.ForeignKey(
#         'products.Product', 
#         on_delete=models.CASCADE
#     )

#     class Meta:
#         # Важно: делаем пару user+product уникальной, чтобы нельзя было добавить товар в избранное дважды
#         unique_together = ('user', 'product')
#         verbose_name = 'Избранное'
#         verbose_name_plural = 'Избранное'

#     def __str__(self):
#         return f'{self.user.username} - {self.product.name}'


# class Address(models.Model):
#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name='addresses'
#     )
#     title = models.CharField(max_length=100, default='Основной адрес')
#     full_address = models.TextField()
#     phone = models.CharField(max_length=20, blank=True, null=True)
#     is_default = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         verbose_name = 'Адрес'
#         verbose_name_plural = 'Адреса'

#     def __str__(self):
#         return f"{self.title} ({self.full_address})"


# class Profile(models.Model):
#     user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     avatar = models.ImageField(
#         upload_to='avatars/',
#         blank=True,
#         null=True,
#         # default лучше задавать в settings.py или в логике view, 
#         # но в модели тоже допустимо, если файл существует в static
#         default='default-avatar.png' 
#     )
#     bio = models.TextField(max_length=500, blank=True)

#     class Meta:
#         verbose_name = 'Профиль'
#         verbose_name_plural = 'Профили'

#     def __str__(self):
#         return f'{self.user.username} Profile'


# class PaymentMethod(models.Model):
#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name='payment_methods'
#     )
#     # ВНИМАНИЕ: Никогда не храните реальные номера карт в открытом виде в БД!
#     # Для примера оставляем, но в продакшене используйте токенизацию (Stripe, YooKassa и т.д.)
#     card_number = models.CharField(max_length=20, verbose_name='Номер карты')
#     is_default = models.BooleanField(default=False, verbose_name='По умолчанию')

#     class Meta:
#         verbose_name = 'Способ оплаты'
#         verbose_name_plural = 'Способы оплаты'

#     def __str__(self):
#         return f"Карта пользователя {self.user.username}"
 
