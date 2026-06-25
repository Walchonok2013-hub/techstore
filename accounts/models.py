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
