from decimal import Decimal
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from products.models import Product
from decimal import Decimal
from django.conf import settings
from products.models import Product

class Cart:
    def __init__(self, request):
        """Инициализация корзины"""
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = {}
            self.session[settings.CART_SESSION_ID] = cart
            self.session.save()
        self.cart = cart  # единое хранилище корзины
    def add(self, product, quantity, update_quantity=False):
        product_id = str(product.id)

    # Валидация quantity
        try:
            quantity = int(quantity)
            if quantity < 0:
                raise ValueError("Количество не может быть отрицательным")
        except (ValueError, TypeError):
            raise ValueError(f"Некорректное значение количества: {quantity}")

        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': quantity,
                'price': str(product.price)
            }
        else:
            if update_quantity:
                self.cart[product_id]['quantity'] = quantity
            else:
                self.cart[product_id]['quantity'] += quantity

        self.save()


    def save(self):
        """Сохраняет корзину в сессию"""
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session.modified = True
        self.session.save()  # важно: сохраняем сессию

    def remove(self, product):
        """Удаляет товар из корзины"""
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        """Перебор элементов корзины и получение товаров из БД"""
        product_ids = self.cart.keys()

    # Получаем товары из БД только если корзина не пуста
        if product_ids:
            products = Product.objects.filter(id__in=product_ids)
        # Создаём словарь товаров по ID для быстрого доступа
            product_dict = {product.id: product for product in products}
        else:
            product_dict = {}

    # Копируем корзину, чтобы не изменять оригинал
        cart_copy = self.cart.copy()

        for product_id, item in cart_copy.items():
            if int(product_id) in product_dict:
            # Добавляем объект товара ТОЛЬКО во временную копию
                temp_item = item.copy()  # создаём копию элемента
                temp_item['product'] = product_dict[int(product_id)]
                temp_item['price'] = Decimal(item['price'])
                temp_item['total_price'] = temp_item['price'] * item['quantity']
                yield temp_item
            else:
            # Если товар не найден в БД, помечаем его как удалённый
                temp_item = item.copy()
                temp_item['product'] = None
                temp_item['price'] = Decimal('0')
                temp_item['total_price'] = Decimal('0')
                yield temp_item


    def __len__(self):
        """Возвращает общее количество товаров в корзине"""
        return sum(item['quantity'] for item in self.cart.values() if isinstance(item, dict))

    def get_total_price(self):
        """Возвращает общую стоимость корзины"""
        total = Decimal('0')
        for item_data in self.cart.values():
            if isinstance(item_data, dict) and 'price' in item_data and 'quantity' in item_data:
                total += Decimal(item_data['price']) * item_data['quantity']
        return total

    def clear(self):
        """Очищает корзину"""
        self.cart.clear()
        self.save()