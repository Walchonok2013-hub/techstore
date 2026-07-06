
from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True) 
    description = models.TextField(blank=True, null=True)
    specifications = models.TextField(
        verbose_name="Характеристики продукта",
        blank=True,
        help_text="Укажите характеристики в формате 'Параметр: значение' через новую строку"
    )
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='products')
    quantity = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    available = models.BooleanField(default=True)
    is_popular = models.BooleanField(default=False, verbose_name='Популярный')
    
    def get_specifications_dict(self):
        if not self.specifications:
            return {}
        specs = {}
        lines = self.specifications.split('\n')
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                specs[key.strip()] = value.strip()
        return specs

    def __str__(self):
        return self.name
    





class Promotion(models.Model):
    name = models.CharField("Название акции", max_length=100)
    is_active = models.BooleanField("Активна", default=True)
    discount_percent = models.PositiveSmallIntegerField("Скидка, %")
    applies_to_category = models.ForeignKey(
        'Category', on_delete=models.CASCADE, null=True, blank=True,
        verbose_name="Категория"
    )
    expires_at = models.DateTimeField("Дата окончания", null=True, blank=True)

    def is_valid(self):
        """Проверяет, активна ли акция прямо сейчас."""
        if not self.is_active:
            return False
        if self.expires_at and self.expires_at < timezone.now():
            return False
        return True

    def get_discount_amount(self, price: Decimal) -> Decimal:
        """
        Считает сумму скидки для данной цены.
        Возвращает Decimal, округлённый до 2 знаков.
        """
        if not self.is_valid():
            return Decimal('0')
        
        discount = price * (Decimal(self.discount_percent) / Decimal('100'))
        return discount.quantize(Decimal('0.01'))

    def __str__(self):
        return f"{self.name} ({self.discount_percent}%)"









