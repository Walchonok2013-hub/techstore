from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from accounts.models import Favorite
from django.contrib.auth import views as auth_views
from techstore import settings
from orders.models import Order
from .models import Profile
from .forms import UserEditForm, ProfileEditForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Sum
from .models import Address 
from django.views.decorators.http import require_http_methods
from .models import Favorite
from orders.models import Order
from products.models import Product
from django.db.models import Avg, Count
from .models import PaymentMethod
from .forms import AddCardForm
import logging
from .forms import CustomUserCreationForm
from django.core.exceptions import ValidationError

from django.shortcuts import render

from django.db.models import Sum, Q
from decimal import Decimal, ROUND_HALF_UP
from orders.models import Order

logger = logging.getLogger(__name__)



@login_required
def toggle_favorite_ajax(request, product_id):
    # 1. Находим товар (если нет - вернет 404)
    product = get_object_or_404(Product, id=product_id)

    # 2. Пытаемся создать запись или получить существующую
    # created будет True, если запись создали только что, и False, если она уже была
    favorite, created = Favorite.objects.get_or_create(
        user=request.user,
        product=product
    )

    # 3. Логика переключения
    if not created:
        # Если запись уже была (created=False) -> значит, убираем из избранного
        favorite.delete()
        action = 'removed'
    else:
        # Если создали только что (created=True) -> значит, добавили
        action = 'added'

    # 4. ВОТ ЭТА СТРОКА: считаем общее количество избранных товаров у пользователя
    # Важно: используем 'user_favorites', так как это значение related_name в модели
    count = request.user.user_favorites.count()

    # 5. Возвращаем JSON ответ для JavaScript
    return JsonResponse({
        'action': action,
        'count': count,  # Это число JS использует для обновления счетчика в шапке
    })


@login_required
def profile(request):
    # 1. Получаем профиль. get_or_create спасает от ошибки, если профиль не создан при регистрации.
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    # 2. Получаем заказы пользователя
    user_orders = Order.objects.filter(user=request.user)
    
    # --- Статистика заказов ---
    total_orders = user_orders.count()
    
    # Сумма потраченного. aggregate всегда возвращает dict, даже если пусто.
    spent_stats = user_orders.aggregate(total_spent=Sum('total_price'))
    total_spent = spent_stats['total_spent'] or 0
    
    # Средний чек. Avg вернет None, если заказов нет.
    avg_check_stats = user_orders.aggregate(average_check=Avg('total_price'))
    average_check = avg_check_stats['average_check'] or 0
    
    # --- Расчет средней скидки (ИСПРАВЛЕННАЯ ЛОГИКА) ---
    discount_stats = user_orders.aggregate(
        total_discount=Sum('discount'),
        total_original=Sum('original_total')
    )
    
    total_discount = discount_stats['total_discount'] or 0
    total_original = discount_stats['total_original'] or 0
    
    # ВАЖНО: Защита от деления на ноль и правильная логика 100% скидки
    if total_original > 0:
        average_discount_percent = (total_discount / total_original) * 100
    else:
        # Если оригинальная сумма 0 (например, все товары были бесплатны или промокоды),
        # считаем скидку 100%, если были применены скидки, или 0%, если скидок не было.
        # В большинстве случаев, если original_total=0, то и discount=0, тогда скидка 0%.
        # Но если логика бизнеса требует иначе - поменяй условие.
        average_discount_percent = 100.0 if total_discount > 0 else 0.0

    # --- Подсчет избранного ---
    # Вариант А: Если у тебя есть отдельная модель Favorite (Рекомендуемый)
    # Раскомментируй эти строки, если модель Favorite существует:
    # from favorites.models import Favorite
    # favorites_count = Favorite.objects.filter(user=request.user).count()
    
    # Вариант Б: Если избранное хранится как M2M поле на модели Product
    # Проверяем наличие атрибута, чтобы view не упал, если связи еще нет в БД
    if hasattr(request.user, 'favorite_products'):
        favorites_count = request.user.favorite_products.count()
    else:
        favorites_count = 0

    # Последние 5 заказов для отображения в таблице (если решишь добавить)
    recent_orders = user_orders.order_by('-created_at')[:5]

    context = {
        'profile': profile,
        'total_orders': total_orders,
        'favorites_count': favorites_count,
        'total_spent': total_spent,
        'average_check': average_check,
        'average_discount_percent': average_discount_percent,
        'recent_orders': recent_orders,
        'has_orders': total_orders > 0, # Удобно для шаблона, чтобы скрыть пустые блоки
    }
    
    return render(request, 'accounts/profile.html', context)

# @login_required
# def profile(request):
#     user = request.user
#     # Получаем все заказы пользователя. Можно добавить фильтр .exclude(status='cancelled'), если нужно
#     orders = Order.objects.filter(user=user)

#     # 1. Считаем потрачено всего и количество заказов
#     total_spent_data = orders.aggregate(total=Sum('total_price'))
#     total_spent = total_spent_data['total'] or Decimal('0.00')
#     total_orders = orders.count()

#     # 2. Считаем средний чек
#     average_check = (
#         (total_spent / total_orders).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
#         if total_orders else Decimal('0.00')
#     )

#     # 3. Считаем среднюю скидку (ПРАВИЛЬНЫЙ СПОСОБ)
#     # Нам нужно посчитать процент скидки для КАЖДОГО заказа, а потом найти среднее
#     discount_percentages = []
    
#     for order in orders:
#         # Защита от деления на ноль, если original_total вдруг 0
#         if order.original_total and order.original_total > 0:
#             percent = (order.discount / order.original_total) * Decimal('100')
#             discount_percentages.append(percent)
    
#     if discount_percentages:
#         # Суммируем все проценты и делим на количество заказов
#         sum_percent = sum(discount_percentages)
#         average_discount_percent = (
#             (sum_percent / len(discount_percentages)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
#         )
#     else:
#         average_discount_percent = Decimal('0.00')

#     # 4. Считаем количество избранного (нужно добавить импорт модели Favorite)
#     # Если у тебя нет модели Favorite, поставь 0 или закомментируй эту строку
#     try:
#         from .models import Favorite
#         favorites_count = Favorite.objects.filter(user=user).count()
#     except ImportError:
#         favorites_count = 0

#     context = {
#         'user_profile': user,
#         'total_spent': total_spent,
#         'orders_count': total_orders,          # В шаблоне используй orders_count, а не total_orders
#         'favorites_count': favorites_count,    # Передаем в шаблон
#         'average_check': average_check,
#         'average_discount_percent': average_discount_percent,
#         'orders': orders[:5]                   # Передаем сами заказы для списка внизу
#     }
    
#     return render(request, 'profile.html', context)

@login_required
def edit_address(request, address_id):
    # Получаем адрес или возвращаем 404, если его нет
    address = get_object_or_404(Address, user=request.user, pk=address_id)

    if request.method == 'POST':
        # Обновляем поля из POST-запроса
        address.title = request.POST.get('title', address.title)
        address.full_address = request.POST.get('full_address', address.full_address)
        address.phone = request.POST.get('phone', address.phone)
        address.notes = request.POST.get('notes', address.notes)
        
        is_default_raw = request.POST.get('is_default')
        is_default = (is_default_raw == 'on')

        # Логика флага "Основной" (аналогично create_address)
        if is_default:
            Address.objects.filter(user=request.user).update(is_default=False)
        elif not Address.objects.filter(user=request.user).exists():
            is_default = True
            
        address.is_default = is_default
        address.save()

        return redirect('accounts:profile_addresses')

    # Если метод GET — показываем форму редактирования
    return render(request, 'accounts/edit_address.html', {'address': address})


@login_required
def profile_addresses(request):
    # Берём только адреса текущего пользователя
    addresses = request.user.addresses.all()
    return render(request, 'accounts/addresses.html', {'addresses': addresses})
@login_required
def delete_address(request, pk):
    # Находим адрес, проверяя, что он принадлежит текущему пользователю
    address = get_object_or_404(Address, pk=pk, user=request.user)

    # Если это основной адрес — запрещаем удаление
    if address.is_default:
        messages.error(request, 'Нельзя удалить основной адрес доставки!')
        return redirect('accounts:profile_addresses')

    # Если не основной — удаляем
    address.delete()
    messages.success(request, 'Адрес успешно удалён.')
    
    return redirect('accounts:profile_addresses')
@login_required
def create_address(request):
    schema = AddressSchema()

    if request.method == 'POST':
        data = {
            'title': request.POST.get('title', ''),
            'full_address': request.POST.get('full_address', ''),
            'phone': request.POST.get('phone', ''),
            'notes': request.POST.get('notes', ''),  # <-- берём из POST, если нет — пустая строка
            'is_default': request.POST.get('is_default') == 'on',
        }

        try:
            validated_data = schema.load(data)
        except ValidationError as err:
            return render(request, 'accounts/create_address.html', {
                'errors': err.messages,
                'form_data': data,
            })

        # Если notes не пришло (или пустое), явно ставим пустую строку
        if 'notes' not in validated_data or validated_data['notes'] is None:
            validated_data['notes'] = ''

        if not request.user.addresses.exists():
            validated_data['is_default'] = True

        Address.objects.create(
            user=request.user,
            **validated_data,
        )

        return redirect('accounts:profile_addresses')

    return render(request, 'accounts/create_address.html')

@login_required
def user_favorites(request):
    # 1. Получаем избранные товары пользователя с предварительной загрузкой связанных товаров
    favorites_qs = Favorite.objects.filter(user=request.user).select_related('product')

    # 2. Настраиваем пагинацию (например, по 8 товаров на страницу)
    paginator = Paginator(favorites_qs, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,      # Ключевая переменная для шаблона (вместо favorites)
        'title': 'Мои избранные товары'
    }
    return render(request, 'accounts/favorites.html', context)
@login_required
def cards_list(request):
    cards = PaymentMethod.objects.filter(user=request.user)
    return render(request, 'accounts/cards_list.html', {'cards': cards})
@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'orders/list.html', {'orders': orders})
@login_required
def add_card(request):
    if request.method == 'POST':
        form = AddCardForm(request.POST)
        if form.is_valid():
            card = form.save(commit=False)
            card.user = request.user
            card.save()
            return redirect('cards_list')
    else:
        form = AddCardForm()
    return render(request, 'accounts/add_card.html', {'form': form})

@login_required
def delete_card(request, pk):
    # Сначала проверяем метод
    if request.method != 'POST':
        return redirect('cards_list')

    # Только потом ищем и удаляем
    card = get_object_or_404(PaymentMethod, pk=pk, user=request.user)
    card.delete()
    
    return redirect('cards_list')



@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Сохраняем сессию, чтобы пользователь не вышел
            messages.success(request, 'Пароль успешно изменён!')
            return redirect('accounts:profile')  # Перенаправляем на профиль
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'accounts/change_password.html', {'form': form})
def login_view(request):
    # КРИТИЧЕСКИ ВАЖНО: при POST-запросе передаем request и request.POST в форму
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        
        if form.is_valid():
            user = form.get_user()
            
            # Дополнительная проверка активности (на всякий случай)
            if not user.is_active:
                messages.error(request, 'Ваш аккаунт деактивирован.')
                return render(request, 'accounts/login.html', {'form': form})
            
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}!')
            
            # Обработка редиректа next
            next_url = request.POST.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('products:home')
        

    else:
        form = AuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    username = request.user.username
    logout(request)
    messages.info(request, f'{username}, Вы успешно вышли из системы')
    return redirect('products:home')


@login_required
def payment_methods_view(request):
    # Берем только карты текущего пользователя
    payment_methods = PaymentMethod.objects.filter(user=request.user)
    
    context = {
        'payment_methods': payment_methods,
        'title': 'Способы оплаты'
    }
    return render(request, 'accounts/payment_methods.html', context)

def payment_methods_add(request):
    if request.method == 'POST':
        # логика обработки добавления карты
        return redirect('accounts:payment-methods-add')  # или другое имя URL
    messages.success(request, 'Карта успешно добавлена')
    return render(request, 'orders/payment_form.html')



@login_required
def profile_view(request):
    # Агрегация данных
    stats = request.user.user_orders.aggregate(
        total_spent=Sum('total_price'),
        orders_count=Count('id'),
        total_discount=Sum('discount'),
        total_original=Sum('original_total'),
    )

    # Безопасное получение значений (защита от None)
    total_spent = stats['total_spent'] or 0
    orders_count = stats['orders_count'] or 0
    total_discount = stats['total_discount'] or 0
    total_original = stats['total_original'] or 0

    # Расчет средней скидки в процентах
    # Формула: (Сумма всех скидок / Сумма всех исходных цен) * 100
    if total_original > 0:
        average_discount_percent = (total_discount / total_original) * 100
    else:
        average_discount_percent = 0

    # Расчет среднего чека
    if orders_count > 0:
        average_check = total_spent / orders_count
    else:
        average_check = 0

    # Считаем избранное
    favorites_count = Favorite.objects.filter(user=request.user).count()

    context = {
        'user': request.user,
        'total_spent': total_spent,
        'orders_count': orders_count,
        'favorites_count': favorites_count,
        'average_discount_percent': average_discount_percent,
        'average_check': average_check,
        # Можно передать сырые данные для отладки, если нужно
        'stats_raw': stats, 
    }

    return render(request, 'accounts/profile.html', context)

# def register_view(request):
#     if request.method == 'POST':
#         form = CustomUserCreationForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             login(request, user)
#             return redirect('products:home')
#     else:
      
#         form = CustomUserCreationForm()
#     return render(request, 'accounts/register.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Вы успешно зарегистрированы!')
            return redirect('products:home')
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})

@login_required
def edit_profile(request):
    user = request.user

    # Гарантированно получаем профиль: создаём, если нет
    profile, created = Profile.objects.get_or_create(user=user)

    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=user)
        profile_form = ProfileEditForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Профиль успешно обновлён!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        user_form = UserEditForm(instance=user)
        profile_form = ProfileEditForm(instance=profile)

    context = {
        'form': user_form,
        'profile_form': profile_form,
        'user': user,
    }
    return render(request, 'accounts/edit_profile.html', context)




@login_required
def settings_view(request):
    return render(request, 'accounts/settings.html')


@login_required
def addresses_view(request):
    addresses = Address.objects.filter(user=request.user)
    return render(request, 'accounts/addresses.html', {'addresses': addresses})


    
def get_default_user_id(apps, schema_editor):
    User = apps.get_model(settings.AUTH_USER_MODEL.split('.')[0], 'User')
    try:
        user = User.objects.get(username='default_user')
        return user.id
    except User.DoesNotExist:
        # Создаём пользователя с хешированным паролем
        user = User.objects.create_user(
            username='default_user',
            email='default@example.com',
            password=None  # или используйте надёжный пароль
        )
        return user.id  
    



@login_required
def user_favorites(request):
    qs = request.user.user_favorites.select_related('product').all()
    paginator = Paginator(qs, 9)  # 9 товаров на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'title': 'Избранное',
        'page_obj': page_obj,
        'wishlist_count': qs.count(),
    }
    return render(request, 'accounts/favorites.html', context)

   