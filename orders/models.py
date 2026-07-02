
from django.db import models
from django.conf import settings
from products.models import Product

STATUS_CHOICES = [
    ('new', 'Новый'),
    ('pending', 'В обработке'),
    ('confirmed', 'Подтверждён'),
    ('shipped', 'Отправлен'),
    ('completed', 'Завершён'),
    ('cancelled', 'Отменён'),
    ('paid', 'Оплачен'),
]

class Order(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,                                           
        related_name='user_orders' 
    )
    
    first_name = models.CharField('Имя', max_length=50, default='')
    last_name = models.CharField('Фамилия', max_length=50, default='')
    email = models.EmailField('Email', default='')       
    phone = models.CharField('Телефон', max_length=20, default='') 
    address = models.CharField('Адрес доставки', max_length=250, default='') 
    notes = models.TextField('Примечания к заказу', blank=True, null=True)
    
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    original_total = models.DecimalField('Полная стоимость', max_digits=10, decimal_places=2, default=0)
    total_price = models.DecimalField('Итого', max_digits=10, decimal_places=2, default=0)
    
    status = models.CharField(
        'Статус', 
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='new'
    )

    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0) 

    def __str__(self):
        # Это исправление решает ошибку AssertionError в тестах
        return f'Order #{self.id}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField('Количество', default=1)

    def __str__(self):
        return f'{self.quantity} x {self.product.name}'

    def get_cost(self):
        return self.price * self.quantity


class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('card', 'Банковская карта'),
        ('cash', 'Наличными при получении'),
        ('online', 'Онлайн‑платёж'),
    ]

    order = models.OneToOneField(
        Order, 
        on_delete=models.CASCADE, 
        verbose_name='Заказ',
        related_name='payment'
    )
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






    
    