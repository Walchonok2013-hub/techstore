from django.test import TestCase
from django.utils import timezone
from decimal import Decimal
from products.models import Product, Category
from promotions.models import Promotion

class ProductDiscountTests(TestCase):
    def setUp(self):
        # Только базовые объекты: категория и товар
        self.category = Category.objects.create(
            name="Смартфоны и аксессуары",
            slug="smartfony-i-aksessuary"
        )
        self.product = Product.objects.create(
            name="Смартфон S24",
            price=Decimal("74999.00"),
            category=self.category,
            is_active=True,
        )

    def test_active_promo_applies_correctly(self):
        promo = Promotion.objects.create(
            name="Скидка 20%",
            discount_percent=Decimal("20"),
            applies_to_category=self.category,
            is_active=True,
            expires_at=timezone.now() + timezone.timedelta(days=7),
        )
        expected = self.product.price * Decimal("0.8")
        result = self.product.get_current_price()
        self.assertEqual(result, expected.quantize(Decimal("0.01")))

    def test_promo_for_other_category_does_not_apply(self):
        other_category = Category.objects.create(
            name="Компьютеры и ноутбуки",
            slug="kompyutery-i-noutbuki"
        )
        promo = Promotion.objects.create(
            name="Скидка на ноутбуки",
            discount_percent=Decimal("10"),
            applies_to_category=other_category,
            is_active=True,
            expires_at=timezone.now() + timezone.timedelta(days=7),
        )
        result = self.product.get_current_price()
        self.assertEqual(result, self.product.price)

    def test_expired_promo_does_not_apply(self):
        promo = Promotion.objects.create(
            name="Просроченная скидка",
            discount_percent=Decimal("50"),
            applies_to_category=self.category,
            is_active=True,
            expires_at=timezone.now() - timezone.timedelta(days=1),
        )
        result = self.product.get_current_price()
        self.assertEqual(result, self.product.price)

    def test_inactive_promo_does_not_apply(self):
        promo = Promotion.objects.create(
            name="Неактивная скидка",
            discount_percent=Decimal("30"),
            applies_to_category=self.category,
            is_active=False,
            expires_at=timezone.now() + timezone.timedelta(days=7),
        )
        result = self.product.get_current_price()
        self.assertEqual(result, self.product.price)

    def test_discount_does_not_make_price_negative(self):
        promo = Promotion.objects.create(
            name="Суперскидка 200%",
            discount_percent=Decimal("200"),
            applies_to_category=self.category,
            is_active=True,
            expires_at=timezone.now() + timezone.timedelta(days=7),
        )
        result = self.product.get_current_price()
        self.assertEqual(result, Decimal("0"))

    def test_no_promo_returns_original_price(self):
        # Никаких акций вообще
        result = self.product.get_current_price()
        self.assertEqual(result, self.product.price)
