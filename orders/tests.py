from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import Order

User = get_user_model()


class OrderModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')

    def test_order_creation(self):
        order = Order.objects.create(user=self.user, status='new')
        # Теперь это сравнение пройдет успешно благодаря __str__ в модели
        self.assertEqual(str(order), f'Order #{order.id}')
        self.assertEqual(order.status, 'new')


class OrderViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')

    def test_my_orders_requires_login(self):
        # Было: reverse('my_orders')
        url = reverse('orders:my_orders') 
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_my_orders_authenticated(self):
        self.client.login(username='testuser', password='12345')
        url = reverse('orders:my_orders')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders/my_orders.html')
