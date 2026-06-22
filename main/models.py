from django.db import models

# Create your models here.
class DeliveryMethod(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    price = models.CharField(max_length=100, verbose_name='Стоимость', blank=True, null=True)
    description = models.TextField(verbose_name='Описание', blank=True, null=True)
    is_active = models.BooleanField(default=True, verbose_name='Активен')


    class Meta:
        verbose_name = 'Способ доставки'
        verbose_name_plural = 'Способы доставки'

    def __str__(self):
        return self.name


class PaymentMethod(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(verbose_name='Описание', blank=True, null=True)
    is_active = models.BooleanField(default=True, verbose_name='Активен')

    class Meta:
        verbose_name = 'Способ оплаты'
        verbose_name_plural = 'Способы оплаты'


    def __str__(self):
        return self.name