from django.db import models
from django.conf import settings
from products.models import Product

class Order(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='user_orders'
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('new', 'Новый'),
            ('paid', 'Оплачен'),
            ('shipped', 'Отправлен'),
            ('completed', 'Завершён'),
        ],
        default='new'
    )
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, default=0) # Полная цена
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0) # Сумма скидки
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f'Заказ #{self.id} от {self.created_at.date()}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name='Товар')
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField('Количество', default=1)

    def get_cost(self):
        return self.price * self.quantity

    def __str__(self):
        return f'{self.quantity} x {self.product.name}'

    class Meta:
        verbose_name = 'Элемент заказа'
        verbose_name_plural = 'Элементы заказа'


class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('card', 'Банковская карта'),
        ('cash', 'Наличными при получении'),
        ('online', 'Онлайн‑платёж'),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, verbose_name='Заказ')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, verbose_name='Способ оплаты')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Сумма')
    transaction_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='ID транзакции')
    is_completed = models.BooleanField(default=False, verbose_name='Оплата завершена')
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name='Дата завершения')

    def __str__(self):
        return f'Оплата для заказа #{self.order.id}'

    class Meta:
        verbose_name = 'Платёж'
        verbose_name_plural = 'Платежи'

# class Product(models.Model):
#     name = models.CharField(max_length=200, verbose_name="Название")
#     price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
#     in_stock = models.BooleanField(default=True, verbose_name="В наличии")
#     slug = models.SlugField(max_length=200, unique=True, blank=True, verbose_name="Slug")
#     created = models.DateTimeField('Создано', auto_now_add=True)

#     def save(self, *args, **kwargs):
#         if not self.slug:
#             from django.utils.text import slugify
#             self.slug = slugify(self.name)
#         super().save(*args, **kwargs)

#     def __str__(self):
#         return self.name

#     class Meta:
#         verbose_name = "Товар"
#         verbose_name_plural = "Товары"




    
    