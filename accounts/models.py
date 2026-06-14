
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class User(AbstractUser):
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        default='avatars/default-avatar.png'
    )
    bio = models.TextField(blank=True)



    # дополнительные поля при необходимости
    phone = models.CharField(max_length=20, blank=True)
    
    class Meta:
        # убедитесь, что имя приложения указано верно
        pass   
    def __str__(self):
        return self.username   
    
    
class Order(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders_from_accounts'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Заказ #{self.id} от {self.created_at.date()}'

class WishlistItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # product = models.ForeignKey('catalog.Product', on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} — {self.product.name}'

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.street}, {self.city}, {self.country}'


class PaymentMethod(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payment_methods')
    # В реальности тут будет token/id платёжного сервиса
    card_last_four = models.CharField('Последние 4 цифры', max_length=4)
    brand = models.CharField('Тип карты', max_length=20, blank=True)
    expiry_month = models.PositiveSmallIntegerField('Месяц')
    expiry_year = models.PositiveSmallIntegerField('Год')
    is_default = models.BooleanField('По умолчанию', default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Способ оплаты'
        verbose_name_plural = 'Способы оплаты'

    def __str__(self):
        return f'{self.brand} ****{self.card_last_four}'
# class PaymentMethod(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     last_digits = models.CharField(max_length=4)
#     is_default = models.BooleanField(default=False)    
#     name = models.CharField(max_length=100, verbose_name='Название способа оплаты')
#     description = models.TextField(blank=True, verbose_name='Описание')
#     is_active = models.BooleanField(default=True, verbose_name='Активен')
#     fee_percent = models.DecimalField(
#         max_digits=5,
#         decimal_places=2,
#         default=0,
#         verbose_name='Комиссия (%)'
#     )
#     created_at = models.DateTimeField(auto_now_add=True)

    # class Meta:
    #     verbose_name = 'Способ оплаты'
    #     verbose_name_plural = 'Способы оплаты'

    # def __str__(self):
    #     return self.name