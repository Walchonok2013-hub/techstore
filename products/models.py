
from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
from promotions.models import Promotion
import logging

logger = logging.getLogger(__name__)

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
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    quantity = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    available = models.BooleanField(default=True)
    is_popular = models.BooleanField(default=False, verbose_name='Популярный')



    def get_current_price(self) -> Decimal:
        now = timezone.now()

        logger.info(
            "[get_current_price] Товар: %s, ID категории: %s, цена в БД: %s",
            self.name, self.category_id, self.price
        )

        # Чётко: та же категория, is_active=True, expires_at >= now
        active_promo = Promotion.objects.filter(
            applies_to_category_id=self.category_id,
            is_active=True,
            expires_at__gte=now,
        ).first()

        if active_promo and active_promo.discount_percent:
            # Используем метод get_discount_amount, если он есть
            discount = active_promo.get_discount_amount(self.price)
            final_price = self.price - discount
            # Защита от отрицательной цены
            final_price = max(final_price, Decimal('0'))
            final_price = final_price.quantize(Decimal('0.01'))

            logger.info(
                "[get_current_price] Найдена акция: %s, скидка %s%%, итоговая цена: %s",
                active_promo.name, active_promo.discount_percent, final_price
            )
            return final_price

        # Для отладки: покажем активные акции вообще (без эмодзи)
        all_active = Promotion.objects.filter(is_active=True)
        promo_info = ", ".join(
            f"{p.name} (cat_id={p.applies_to_category_id})"
            for p in all_active
        )
        logger.debug(
            "[get_current_price] Подходящая акция не найдена для категории %s. Активные акции: [%s]",
            self.category_id, promo_info
        )

        return self.price

    def get_original_price_for_order(self) -> Decimal:
        """
        Для чека: если есть акция — показываем исходную цену (self.price),
        иначе тоже self.price.
        В твоём случае 'полная цена' — это просто self.price,
        а скидка считается динамически.
        """
        return self.price

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
    










