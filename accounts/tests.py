from django.test import TestCase, Client
from django.urls import reverse, resolve
from django.contrib.auth import get_user_model
from django.utils.text import slugify

from accounts.models import Favorite, Address, PaymentMethod, Profile
from products.models import Product, Category

User = get_user_model()


class ModelTests(TestCase):
    def setUp(self):
        # 1. Создаём тестового пользователя для моделей
        self.user = User.objects.create_user(
            username='testuser_model',
            email='test@example.com',
            password='password123'
        )

        # 2. Создаём категорию (обязательно для Product)
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )

        # 3. Создаём продукт с правильными полями
        self.product = Product.objects.create(
            name='Test Product',
            slug=slugify('Test Product'),
            price=100.00,
            description='Test description',
            category=self.category,
            quantity=10,
            is_active=True,
            available=True
        )


    def test_profile_creation(self):
    # Профиль создаётся автоматически через сигнал post_save
        profile = self.user.profile

        self.assertEqual(str(profile), f'Профиль {self.user.username}')
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.bio, '')

    # Правильная проверка для ImageField, который может быть пустым
        self.assertFalse(profile.avatar)
    # либо: self.assertEqual(profile.avatar.name, '')

    def test_favorite_creation(self):
        favorite = Favorite.objects.create(user=self.user, product=self.product)
        self.assertEqual(str(favorite), 'testuser_model - Test Product')
        self.assertEqual(favorite.user, self.user)
        self.assertEqual(favorite.product, self.product)

    def test_address_creation(self):
        address = Address.objects.create(
            user=self.user,
            title='Home',
            full_address='123 Main St',
            phone='+79990000000',
            is_default=True
        )
        self.assertEqual(str(address), 'Home (123 Main St)')
        self.assertTrue(address.is_default)

    def test_payment_method_creation(self):
        payment = PaymentMethod.objects.create(
            user=self.user,
            card_number='1234567890123456',
            is_default=True
        )
        self.assertEqual(str(payment), 'Карта пользователя testuser_model')
        self.assertTrue(payment.is_default)


class UrlTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Используем ДРУГОЕ имя пользователя, чтобы избежать конфликта UNIQUE
        self.user = User.objects.create_user(
            username='testuser_url',
            password='password123'
        )

    def test_login_url(self):
        url = reverse('accounts:login')
        self.assertEqual(url, '/accounts/login/')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_logout_url(self):
        url = reverse('accounts:logout')
        self.assertEqual(url, '/accounts/logout/')
        response = self.client.get(url)
        self.assertIn(response.status_code, [200, 302])

    def test_profile_url(self):
        url = reverse('accounts:profile')
        self.assertEqual(url, '/accounts/profile/')
        # Логинимся под testuser_url
        self.client.login(username='testuser_url', password='password123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_edit_profile_url(self):
        url = reverse('accounts:edit_profile')
        self.assertEqual(url, '/accounts/edit-profile/')
        self.client.login(username='testuser_url', password='password123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_register_url(self):
        url = reverse('accounts:register')
        self.assertEqual(url, '/accounts/register/')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_addresses_urls(self):
        self.client.login(username='testuser_url', password='password123')
        
        # Список адресов
        url = reverse('accounts:profile_addresses')
        self.assertEqual(url, '/accounts/addresses/')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Создание адреса
        url = reverse('accounts:create_address')
        self.assertEqual(url, '/accounts/addresses/create/')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Проверка резолва динамического URL
        resolver = resolve('/accounts/addresses/1/delete/')
        self.assertEqual(resolver.view_name, 'accounts:delete_address')

    def test_payment_methods_urls(self):
        self.client.login(username='testuser_url', password='password123')
        
        url = reverse('accounts:payment_methods')
        self.assertEqual(url, '/accounts/payment-methods/')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        url = reverse('accounts:payment-methods-add')
        self.assertEqual(url, '/accounts/payment-methods/add/')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_favorites_urls(self):
        self.client.login(username='testuser_url', password='password123')
        
        url = reverse('accounts:favorites')
        self.assertEqual(url, '/accounts/favorites/')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        resolver = resolve('/accounts/favorites/1/toggle/')
        self.assertEqual(resolver.view_name, 'accounts:toggle_favorite')

    def test_password_reset_urls(self):
        url = reverse('accounts:password_reset')
        self.assertEqual(url, '/accounts/password-reset/')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        url = reverse('accounts:password_reset_done')
        self.assertEqual(url, '/accounts/password-reset/done/')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)       
