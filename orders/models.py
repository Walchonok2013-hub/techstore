
from django.db import models
from django.conf import settings
from products.models import Product
from decimal import Decimal
import calendar
from django.utils import timezone

STATUS_CHOICES = [
    ('new', 'Новый'),
    ('pending', 'В обработке'),
    ('confirmed', 'Подтверждён'),
    ('shipped', 'Отправлен'),
    ('completed', 'Завершён'),
    ('cancelled', 'Отменён'),
    ('paid', 'Оплачен'),
]

PAYMENT_TYPE_CHOICES = [
    ('card', 'Банковская карта'),
    ('cash', 'При получении'),
    ('online', 'Онлайн‑платёж'),
]

class Order(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,          
        related_name='user_orders',
        null=True,
        blank=True,
        verbose_name='Пользователь'
    )
    
    first_name = models.CharField('Имя', max_length=50, default='')
    last_name = models.CharField('Фамилия', max_length=50, default='')
    email = models.EmailField('Email', default='')       
    phone = models.CharField('Телефон', max_length=20, default='') 
    address = models.CharField('Адрес доставки', max_length=250, default='') 
    notes = models.TextField('Примечания к заказу', blank=True, null=True)
    
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    
    # Эти поля хранят итоговые суммы
    original_total = models.DecimalField('Полная стоимость', max_digits=10, decimal_places=2, default=Decimal('0'))
    total_price = models.DecimalField('Итого', max_digits=10, decimal_places=2, default=Decimal('0'))
    discount = models.DecimalField('Сумма скидки', max_digits=10, decimal_places=2, default=Decimal('0')) 
    
    status = models.CharField(
        'Статус', 
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='new'
    )


    payment_type = models.CharField(
        'Способ оплаты',
        max_length=20,
        choices=PAYMENT_TYPE_CHOICES,
        default='cash'                  
    )
    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'  
        ordering = ['-created_at']
        
    def __str__(self):
        return f'Заказ №{self.id}'

    def recalculate_totals(self):
        total_original = Decimal('0')
        total_discount = Decimal('0')
        total_final = Decimal('0')

        for item in self.items.all():
            total_original += item.original_price * item.quantity
            total_final += item.price * item.quantity
            total_discount += (item.original_price - item.price) * item.quantity

        self.original_total = total_original
        self.discount = total_discount
        self.total_price = total_final
        self.save(update_fields=['original_total', 'discount', 'total_price'])
        


class OrderItem(models.Model):
    order = models.ForeignKey(
        'orders.Order',
        related_name='items',
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.PROTECT  # Защита от удаления товара, если есть заказы
    )

    # Цена, по которой товар был куплен (со всеми скидками)
    final_price = models.DecimalField(
        'Цена со скидкой (на момент покупки)',
        max_digits=10,
        decimal_places=2,
    )

    # Полная цена товара без скидок (для отображения экономии)
    original_price = models.DecimalField(
        'Полная цена (без скидок)',
        max_digits=10,
        decimal_places=2,
    )

    quantity = models.PositiveIntegerField('Количество', default=1)

    @property
    def discount_amount(self):
        """Сумма скидки для этой позиции"""
        # Защита от отрицательного значения, если вдруг цены перепутают
        return max((self.original_price - self.final_price) * self.quantity, Decimal('0'))

    @property
    def get_cost(self):
        """Итоговая стоимость позиции (final_price * quantity)"""
        return self.final_price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product.name} ({self.get_cost:.2f} ₽)"
    
    class Meta:
        verbose_name = ('Позиция заказа')
        verbose_name_plural = ('Позиции заказа')


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
        return f'Оплата заказа №{self.order.id}'

    class Meta:
        verbose_name = 'Платёж'
        verbose_name_plural = 'Платежи'






    
    