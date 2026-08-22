from decimal import Decimal
from django.conf import settings
from products.models import Product


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = {}
            self.session[settings.CART_SESSION_ID] = cart
            self.session.save()
        self.cart = cart

    def add(self, product, quantity=1, update_quantity=False, original_price=None):
        product_id = str(product.id)

        # Валидация количества
        try:
            quantity = int(quantity)
            if quantity < 0:
                raise ValueError("Количество не может быть отрицательным")
        except (ValueError, TypeError):
            raise ValueError(f"Некорректное значение количества: {quantity}")

        if original_price is None:
            original_price = product.price

        price_with_discount = product.get_current_price()

        if product_id not in self.cart:
            # Добавляем новый товар
            total_price_value = price_with_discount * quantity
            self.cart[product_id] = {
                'quantity': quantity,
                'price': str(price_with_discount),
                'original_price': str(original_price),
                'total_price': str(total_price_value),
                'name': product.name,
            }
        else:
            # Обновляем существующий товар
            if update_quantity:
                self.cart[product_id]['quantity'] = quantity
            else:
                self.cart[product_id]['quantity'] += quantity

            # Обязательно обновляем цену и original_price
            self.cart[product_id]['price'] = str(price_with_discount)
            self.cart[product_id]['original_price'] = str(original_price)

            # Пересчитываем итоговую цену строки
            current_price = Decimal(self.cart[product_id]['price'])
            new_total = current_price * self.cart[product_id]['quantity']
            self.cart[product_id]['total_price'] = str(new_total)

        self.save()

    def save(self):
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session.modified = True

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        product_ids = self.cart.keys()
        products = {}

        if product_ids:
            products = {str(p.id): p for p in Product.objects.filter(id__in=product_ids)}

        for product_id, item in self.cart.items():
            product = products.get(product_id)

            yield {
                'product_id': int(product_id),
                'name': item.get('name', 'Товар удалён'),
                'quantity': item['quantity'],
                'price': Decimal(item['price']),
                'original_price': Decimal(item.get('original_price', item['price'])),
                'total_price': Decimal(item['price']) * item['quantity'],
                'product': product
            }

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        total = Decimal('0')
        for item in self.cart.values():
            total += Decimal(item['price']) * item['quantity']
        return total

    def clear(self):
        self.cart.clear()
        self.save()

    def get_total_quantity(self):
        return sum(item['quantity'] for item in self.cart.values())  


    
  
