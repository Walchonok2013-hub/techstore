from decimal import Decimal
from django.test import TestCase, Client
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from products.models import Product, Category
from promotions.models import Promotion
from django.contrib.auth import get_user_model
from django.urls import reverse 

User = get_user_model()

class CartTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='testuser',
            password='password123'
        )

        cls.category = Category.objects.create(
            name='Телефоны',
            slug='phones'
        )

        cls.product = Product.objects.create(
            name='iPhone',
            slug='iphone',
            category=cls.category,
            price=Decimal('1000.00'),
            quantity=10,
            is_active=True,
            available=True
        )
        
        # 👇 НОВЫЙ ТОВАР СО СКИДКОЙ
        cls.product_on_sale = Product.objects.create(
            name='iPhone (Акция!)',
            slug='iphone-sale',
            category=cls.category,
            price=Decimal('1000.00'),
            quantity=10,
            is_active=True,
            available=True,
            discount=Decimal('200.00')  # Скидка 200 ₽
        )        

 

    def setUp(self):
        self.client = Client()
        # 👇 ЭТО КРИТИЧНО: логиним пользователя перед каждым тестом
        self.client.login(username='testuser', password='password123')

        # Пересоздаём URL-ы в setUp, потому что reverse может не сработать в setUpTestData
        self.cart_detail_url = reverse('cart:cart_detail')
        self.add_url = lambda pid: reverse('cart:cart_add', args=[pid])
        self.remove_url = lambda pid: reverse('cart:cart_remove', args=[pid])
        self.ajax_url = reverse('cart:cart_ajax')



    # --- Тест 1: Добавление товара в пустую корзину ---
    def test_add_to_empty_cart(self):
        response = self.client.post(self.add_url(self.product.id))
        self.assertRedirects(response, self.cart_detail_url)

        session = self.client.session
        cart_data = session.get('cart', {})
        self.assertIn(str(self.product.id), cart_data)
        self.assertEqual(cart_data[str(self.product.id)]['quantity'], 1)

    # --- Тест 2: Повторное добавление товара (увеличение количества) ---
    def test_add_same_product_twice(self):
        self.client.post(self.add_url(self.product.id))

        response = self.client.post(self.add_url(self.product.id))
        self.assertEqual(response.status_code, 302)

        session = self.client.session
        cart_data = session.get('cart', {})
        self.assertEqual(cart_data[str(self.product.id)]['quantity'], 2)

    # --- Тест 3: Удаление товара из корзины ---

    def test_remove_from_cart(self):
        # Сначала добавляем товар
        self.client.post(self.add_url(self.product.id))

        # Потом удаляем
        response = self.client.post(self.remove_url(self.product.id))
        # Вместо assertRedirects — явная проверка
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.cart_detail_url)

        # Проверяем, что товара больше нет в сессии
        session = self.client.session
        cart_data = session.get('cart', {})
        self.assertNotIn(str(self.product.id), cart_data)

    # --- Тест 4: AJAX‑эндпоинт корзины (cart_ajax) ---
    def test_cart_ajax_endpoint(self):
        self.client.post(self.add_url(self.product.id))

        response = self.client.get(self.ajax_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')

        data = response.json()
        self.assertIn('items_count', data)
        self.assertIn('total_price', data)
        self.assertGreaterEqual(data['items_count'], 1)
        self.assertTrue(Decimal(data['total_price']) > 0)

    # --- Тест 5: Попытка добавить несуществующий товар ---
    def test_add_nonexistent_product(self):
        non_existent_id = 99999
        response = self.client.post(self.add_url(non_existent_id))

        # ВАЖНО: если в views.cart_add стоит get_object_or_404 — будет 404
        # Если стоит try/except и редирект — будет 302
        # Ниже вариант под 404. Если у тебя редирект, замени на assertRedirects
        self.assertEqual(response.status_code, 404)

    # --- Тест 6: Страница корзины с товарами (авторизованный пользователь) ---
    def test_cart_detail_page(self):
        self.client.force_login(self.user)

        response_add = self.client.post(self.add_url(self.product.id))
        self.assertRedirects(response_add, self.cart_detail_url)

        response = self.client.get(self.cart_detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cart/detail.html')
        self.assertIn('cart_items', response.context)
        self.assertIn('total_items', response.context)
        self.assertIn('total_price', response.context)

        cart_items = response.context['cart_items']
        self.assertTrue(len(cart_items) > 0)
        self.assertEqual(cart_items[0]['quantity'], 1)

    # --- Тест 7: Пустая корзина → редирект на каталог ---

    def test_cart_detail_empty_redirects_to_catalog(self):
    # Очищаем сессию, чтобы корзина была пустой
        session = self.client.session
        session['cart'] = {}
        session.save()

        response = self.client.get(self.cart_detail_url)

        if hasattr(self, 'products_app_name_used') or True:

            self.assertRedirects(response, reverse('products:catalog'))

    
    # --- Тест 8: Коррумпированная сессия корзины ---
    def test_corrupted_cart_session(self):
        session = self.client.session
        session['cart'] = {'123': 'invalid_data'}
        session.save()

        response = self.client.get(self.cart_detail_url)
        # Если твой view делает redirect при битой корзине — тут должен быть 302
        self.assertEqual(response.status_code, 302)
       
        self.assertEqual(response.url, reverse('products:catalog'))
        
        # --- Тест 9: Добавление товара со скидкой (цена в сессии) ---
    def test_add_product_with_discount_saves_correct_price(self):
        # 1. Получаем сессию клиента
        session = self.client.session
        
        # 2. Принудительно очищаем корзину и сохраняем
        session['cart'] = {}
        session.save()
        
        # 3. Делаем POST-запрос на добавление товара
        response = self.client.post(self.add_url(self.product_on_sale.id))
        
        # 4. ВАЖНО: После запроса нужно явно загрузить обновленную сессию!
        # self.client.session автоматически не обновляется после запроса в некоторых версиях Django
        self.client.session.modified = True
        self.client.session.save()
        
        # 5. Теперь берем данные из сессии заново
        cart_data = self.client.session.get('cart', {})
        item = cart_data.get(str(self.product_on_sale.id))
        
        # 6. Проверка на случай, если товар вообще не добавился
        self.assertIsNotNone(item, "Товар не был добавлен в корзину")
        
        # 7. Финальная проверка
        # Используем Decimal для сравнения цен, как у тебя в тесте
        from decimal import Decimal
        self.assertEqual(Decimal(item['original_price']), self.product_on_sale.price)

    # --- Тест 10: Итоговый расчет суммы в корзине (с учетом скидки) ---
    def test_cart_total_price_with_discount(self):
        """Проверяем, что общая сумма корзины считается верно"""
        # Добавляем товар со скидкой
        self.client.post(self.add_url(self.product_on_sale.id))
        
        # Делаем запрос на страницу корзины, чтобы view посчитал total_price
        response = self.client.get(self.cart_detail_url)
        
        self.assertEqual(response.status_code, 200)
        
        # Получаем контекст из ответа
        total_price = response.context.get('total_price')
        
        # Ожидаемая сумма: (1000 - 200) * 1 = 800
        expected_total = self.product_on_sale.get_current_price() * 1
        
        self.assertEqual(total_price, expected_total)

    # --- Тест 11: Проверка AJAX-ответа (сумма со скидкой) ---
    def test_ajax_cart_returns_correct_total_with_discount(self):
        """Проверяем, что AJAX-эндпоинт возвращает верную сумму со скидкой"""
        self.client.post(self.add_url(self.product_on_sale.id))
        
        response = self.client.get(self.ajax_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        data = response.json()
        
        # Проверяем наличие полей
        self.assertIn('total_price', data)
        self.assertIn('items_count', data)
        
        # Сравниваем суммы
        expected_total = self.product_on_sale.get_current_price() * 1
        # В JSON числа могут приходить как float, поэтому приводим к Decimal для сравнения
        self.assertEqual(Decimal(str(data['total_price'])), expected_total)
        self.assertEqual(data['items_count'], 1)

    # --- Тест 12: Обновление количества не сбрасывает скидку ---
    def test_update_quantity_keeps_discounted_price(self):
        """При повторном добавлении (update) цена со скидкой должна сохраниться"""
        # Добавляем товар
        self.client.post(self.add_url(self.product_on_sale.id))
        
        # Добавляем ещё раз (увеличиваем количество)
        response = self.client.post(self.add_url(self.product_on_sale.id))
        self.assertRedirects(response, self.cart_detail_url)
        
        session = self.client.session
        cart_data = session.get('cart', {})
        item = cart_data.get(str(self.product_on_sale.id))
        
        self.assertEqual(item['quantity'], 2)
        # Цена должна остаться со скидкой (800), а не стать полной (1000)
        self.assertEqual(item['price'], str(self.product_on_sale.get_current_price()))    
