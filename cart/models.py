from django.db import models
from django.conf import settings
from products.models import Product

class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='cart'  # Удобно обращаться как user.cart
    )
    session_key = models.CharField(max_length=40, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return f"Cart {self.id} (User: {self.user})"

    @classmethod
    def get_cart(cls, request):
        """
        Умный поиск корзины:
        1. Если пользователь авторизован -> берем его корзину из БД.
        2. Если гость -> ищем по session_key или создаем новую.
        """
        if request.user.is_authenticated:
            # get_or_create вернет существующую корзину пользователя или создаст новую
            cart, _ = cls.objects.get_or_create(user=request.user)
            return cart
        
        # Логика для гостя
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key

        # Ищем корзину по ключу сессии
        cart, created = cls.objects.get_or_create(session_key=session_key)
        
        # Если корзина только что создана, сохраняем session_key в модель
        if created:
            cart.session_key = session_key
            cart.save(update_fields=['session_key'])
            
        return cart
    
    def __str__(self):
        return f"Cart {self.id}"   


    def get_total_price(self):
        """Считает общую сумму товаров в корзине"""
        return sum(item.product.price * item.quantity for item in self.items.all())
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    
    @property
    def total_price(self):
        """Возвращает общую стоимость позиции (цена * кол-во)"""
        return self.product.price * self.quantity

    class Meta:
        # Гарантирует, что в одной корзине не будет двух записей одного товара
        unique_together = ('cart', 'product')

