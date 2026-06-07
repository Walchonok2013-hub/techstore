from django.db import models
from django.conf import settings
from decimal import Decimal

class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    in_stock = models.BooleanField(default=True, verbose_name="В наличии")
    slug = models.SlugField(max_length=200, unique=True, blank=True, verbose_name="Slug")
    created = models.DateTimeField('Создано', auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"


class Order(models.Model):
    ORDER_STATUS_CHOICES = (
        ('NEW', 'Новый'),
        ('PAID', 'Оплачен'),
        ('SHIPPED', 'Отправлен'),
        ('DONE', 'Выполнен'),
    )
    status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS_CHOICES,
        default='NEW',
        null=False,
        blank=False
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name="Пользователь",
        null=True,  # Временное разрешение NULL для отладки
        blank=True   # Временное разрешение blank для отладки
    )
    first_name = models.CharField(max_length=50, verbose_name="Имя")
    last_name = models.CharField(max_length=50, verbose_name="Фамилия")
    email = models.EmailField(verbose_name="Email")
    address = models.TextField(verbose_name="Адрес")
    postal_code = models.CharField(max_length=20, verbose_name="Почтовый индекс")
    city = models.CharField(max_length=100, verbose_name="Город")
    created = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
    updated = models.DateTimeField(auto_now=True, verbose_name="Обновлён")
    paid = models.BooleanField(default=False, verbose_name="Оплачен")
   
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Общая сумма"
    )

    def __str__(self):
        return f"Заказ #{self.id} от {self.user.username if self.user else 'анонимный'}"

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-created']


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар")
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField('Количество', default=1)

    def get_cost(self):
        return self.price * self.quantity

    def __str__(self):
        return f'{self.quantity} x {self.product.name}'

    class Meta:
        verbose_name = "Элемент заказа"
        verbose_name_plural = "Элементы заказа"


class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('card', 'Банковская карта'),
        ('cash', 'Наличными при получении'),
        ('online', 'Онлайн‑платёж'),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE, verbose_name="Заказ")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, verbose_name="Способ оплаты")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма")
    transaction_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="ID транзакции")
    is_completed = models.BooleanField(default=False, verbose_name="Оплата завершена")
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name="Дата завершения")

    def __str__(self):
        return f"Оплата для заказа #{self.order.id}"

    class Meta:
        verbose_name = "Платёж"
        verbose_name_plural = "Платежи"

# from django.db import models
# from django.conf import settings
# from products.models import Product
# from decimal import Decimal
# from django.contrib.auth.models import User

# from decimal import Decimal

# class Order(models.Model):
#     ORDER_STATUS_CHOICES = (
#         ('NEW', 'Новый'),
#         ('PAID', 'Оплачен'),
#         ('SHIPPED', 'Отправлен'),
#         ('DONE', 'Выполнен'),
#     )
#     status = models.CharField(
#         max_length=20,
#         choices=ORDER_STATUS_CHOICES,
#         default='NEW',
#         null=False,
#         blank=False
#     )
#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name='orders',
#         verbose_name="Пользователь",
#         null=True,  # Временное разрешение NULL для отладки
#         blank=True   # Временное разрешение blank для отладки
#     )
#     first_name = models.CharField(max_length=50, verbose_name="Имя")
#     last_name = models.CharField(max_length=50, verbose_name="Фамилия")
#     email = models.EmailField(verbose_name="Email")
#     address = models.TextField(verbose_name="Адрес")
#     postal_code = models.CharField(max_length=20, verbose_name="Почтовый индекс")
#     city = models.CharField(max_length=100, verbose_name="Город")
#     created = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
#     updated = models.DateTimeField(auto_now=True, verbose_name="Обновлён")
#     paid = models.BooleanField(default=False, verbose_name="Оплачен")
    
#     status = models.CharField(max_length=10, choices=ORDER_STATUS_CHOICES, default='NEW')
#     total_amount = models.DecimalField(
#         max_digits=10,
#         decimal_places=2,
#         default=Decimal('0.00'),
#         verbose_name="Общая сумма"
#     )

#     def __str__(self):
#         return f"Заказ #{self.id} от {self.user.username}"

#     class Meta:
#         verbose_name = "Заказ"
#         verbose_name_plural = "Заказы"
#         ordering = ['-created']



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




# class Order(models.Model):
#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,  # Вместо auth.User
#         on_delete=models.CASCADE,
#         related_name='orders',
#         verbose_name="Пользователь"
#     )
#     first_name = models.CharField('Имя', max_length=50)
#     last_name = models.CharField('Фамилия', max_length=50)
#     email = models.EmailField()
#     address = models.CharField('Адрес', max_length=250)
#     postal_code = models.CharField('Почтовый индекс', max_length=20)
#     city = models.CharField('Город', max_length=100)
#     created = models.DateTimeField('Создано', auto_now_add=True)
#     updated = models.DateTimeField('Обновлено', auto_now=True)
#     paid = models.BooleanField('Оплачено', default=False)

#     class Meta:
#         ordering = ['-created']
#         verbose_name = 'Заказ'
#         verbose_name_plural = 'Заказы'

#     def __str__(self):
#         return f'Заказ {self.id}'

# class OrderItem(models.Model):
#     order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
#     product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар")
#     price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
#     quantity = models.PositiveIntegerField('Количество', default=1)

#     def get_cost(self):
#         return self.price * self.quantity

#     def __str__(self):
#         return f'{self.quantity} x {self.product.name}'

# class OrderItem(models.Model):
#     order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name="Заказ")
#     product = models.ForeignKey(
#         'Product',  # укажите полное имя модели
#         on_delete=models.CASCADE,
#         verbose_name="Товар",
#         related_name='orders_order_items'  # уникальный related_name
#     )
#     quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")
#     price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")

#     def __str__(self):
#         return f"{self.quantity} × {self.product.name}"

#     class Meta:
#         verbose_name = "Элемент заказа"
#         verbose_name_plural = "Элементы заказа"

# class Payment(models.Model):
#     PAYMENT_METHOD_CHOICES = [
#         ('card', 'Банковская карта'),
#         ('cash', 'Наличными при получении'),
#         ('online', 'Онлайн‑платёж'),
#     ]

#     order = models.OneToOneField(Order, on_delete=models.CASCADE, verbose_name="Заказ")
#     payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, verbose_name="Способ оплаты")
#     amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма")
#     transaction_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="ID транзакции")
#     is_completed = models.BooleanField(default=False, verbose_name="Оплата завершена")
#     completed_at = models.DateTimeField(blank=True, null=True, verbose_name="Дата завершения")

#     def __str__(self):
#         return f"Оплата для заказа #{self.order.id}"

#     class Meta:
#         verbose_name = "Платёж"
#         verbose_name_plural = "Платежи"
    
    