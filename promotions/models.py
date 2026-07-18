from django.db import models
from django.utils import timezone
from decimal import Decimal

class Promotion(models.Model):
    name = models.CharField("Название акции", max_length=100)
    is_active = models.BooleanField("Активна", default=True)
    discount_percent = models.PositiveSmallIntegerField(
        "Скидка, %",
        help_text="Введите число от 1 до 100 (например, 15 для скидки 15%)"
    )
    applies_to_category = models.ForeignKey(
        'products.Category',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Категория",
        related_name='promotions',
    )
    expires_at = models.DateTimeField("Дата окончания", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)  # <-- важно для сортировки

    def is_valid(self):
        if not self.is_active:
            return False
        if self.expires_at and self.expires_at < timezone.now():
            return False
        return True

    def get_discount_amount(self, price: Decimal) -> Decimal:
        if not self.is_valid():
            return Decimal('0')
        discount = price * (Decimal(self.discount_percent) / Decimal('100'))
        return discount.quantize(Decimal('0.01'))

    def __str__(self):
        return f"{self.name} ({self.discount_percent}%)"
    
    class Meta:
        verbose_name = 'Акция'
        verbose_name_plural = 'Акции'
        ordering = ['-created_at']
