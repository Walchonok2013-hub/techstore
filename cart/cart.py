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

    def add(self, product, quantity, update_quantity=False, original_price=None):
        product_id = str(product.id)

        try:
            quantity = int(quantity)
            if quantity < 0:
                raise ValueError("Количество не может быть отрицательным")
        except (ValueError, TypeError):
            raise ValueError(f"Некорректное значение количества: {quantity}")

        # Если original_price не передан, считаем, что полная цена = текущей цене товара
        if original_price is None:
            original_price = product.price

        if product_id not in self.cart:
            self.cart[product_id] = {
                'quantity': quantity,
                'price': str(product.price),          # цена со скидкой (или текущая)
                'original_price': str(original_price),  # полная цена (до скидки)
                'name': product.name
            }
        else:
            if update_quantity:
                self.cart[product_id]['quantity'] = quantity
            else:
                self.cart[product_id]['quantity'] += quantity

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
                'name': item.get('name', 'Товар удален'),
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

# from decimal import Decimal
# from django.conf import settings
# from django.core.exceptions import ObjectDoesNotExist
# from products.models import Product

# class Cart:
#     def __init__(self, request):
#         self.session = request.session
#         cart = self.session.get(settings.CART_SESSION_ID)
#         if not cart:
#             cart = {}
#             self.session[settings.CART_SESSION_ID] = cart
#             self.session.save()
#         self.cart = cart

#     def add(self, product, quantity, update_quantity=False):
#         product_id = str(product.id)
        
#         try:
#             quantity = int(quantity)
#             if quantity < 0:
#                 raise ValueError("Количество не может быть отрицательным")
#         except (ValueError, TypeError):
#             raise ValueError(f"Некорректное значение количества: {quantity}")

#         if product_id not in self.cart:
#             self.cart[product_id] = {
#                 'quantity': quantity,
#                 'price': str(product.price),
#                 'name': product.name
#             }
#         else:
#             if update_quantity:
#                 self.cart[product_id]['quantity'] = quantity
#             else:
#                 self.cart[product_id]['quantity'] += quantity

#         self.save()

#     def save(self):
#         self.session[settings.CART_SESSION_ID] = self.cart
#         self.session.modified = True

#     def remove(self, product):
#         product_id = str(product.id)
#         if product_id in self.cart:
#             del self.cart[product_id]
#             self.save()

#     def __iter__(self):
#         product_ids = self.cart.keys()
#         products = {}
        
#         if product_ids:
#             products = {str(p.id): p for p in Product.objects.filter(id__in=product_ids)}

#         for product_id, item in self.cart.items():
#             product = products.get(product_id)
            
#             yield {
#                 'product_id': int(product_id),
#                 'name': item.get('name', 'Товар удален'),
#                 'quantity': item['quantity'],
#                 'price': Decimal(item['price']),
#                 'total_price': Decimal(item['price']) * item['quantity'],
#                 'product': product
#             }

#     def __len__(self):
#         return sum(item['quantity'] for item in self.cart.values())

#     def get_total_price(self):
#         total = Decimal('0')
#         for item in self.cart.values():
#             total += Decimal(item['price']) * item['quantity']
#         return total

#     def clear(self):
#         self.cart.clear()
#         self.save()

    
  
