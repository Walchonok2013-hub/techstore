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
from .forms import UserEditForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Sum
from .models import Address 
from django.views.decorators.http import require_http_methods
from .models import Favorite
from products.models import Product
from django.db.models import Sum, Avg, Count
from .models import PaymentMethod
from .forms import AddCardForm
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
def orders_view(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'orders': orders,
    }
    return render(request, 'accounts/orders.html', context)
@login_required
def profile(request):
    # Используем данные напрямую из request.user
    orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    total_orders = orders.count()
    total_spent = sum(order.total_price for order in orders)
    average_check = total_spent / total_orders if total_orders else 0
    
    context = {
        'user': request.user,  # вместо profile
        'orders': orders,
        'total_orders': total_orders,
        'total_spent': total_spent,
        'average_check': average_check,
    }
    return render(request, 'accounts/profile.html', context)
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
    if request.method == 'POST':
        title = request.POST.get('title', '')
        full_address = request.POST.get('full_address', '')
        phone = request.POST.get('phone', '')
        notes = request.POST.get('notes', '')
        is_default = request.POST.get('is_default') == 'on'  # checkbox приходит как 'on' или отсутствует

        # Если это первый адрес пользователя, можно сразу сделать его основным
        if not request.user.addresses.exists():
            is_default = True

        address = Address.objects.create(
            user=request.user,
            title=title,
            full_address=full_address,
            phone=phone,
            notes=notes,
            is_default=is_default
        )
        return redirect('accounts:profile_addresses')

    return render(request, 'accounts/create_address.html')
#@login_required
# def user_favorites(request):
#     # Получаем избранные товары пользователя с предварительной загрузкой связанных товаров
#     favorites = Favorite.objects.filter(user=request.user).select_related('product')
#     context = {
#         'favorites': favorites,
#         'title': 'Мои избранные товары'
#     }
#     return render(request, 'accounts/favorites.html', context)
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
# @login_required
# def delete_card(request, pk):
#     # Проверяем, что карта принадлежит текущему пользователю
#     card = get_object_or_404(PaymentMethod, pk=pk, user=request.user)
#     if request.method == 'POST':
#         card.delete()
#         return redirect('cards_list')
#     # Если зашли не через POST (например, по прямой ссылке), просто возвращаем в список
#     return redirect('cards_list')


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
            return redirect('products:home') # Или другое имя вашего главного URL
        
        # Если форма невалидна, мы просто рендерим её снова.
        # Ошибки уже внутри form.errors и отобразятся в шаблоне.
        # НЕ добавляйте здесь messages.error с общим текстом, это скроет реальные ошибки.
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

    # Статистика по заказам
    stats = request.user.user_orders.aggregate(
        total_spent=Sum('total_price'),
        average_order=Avg('total_price'),
        orders_count=Count('id'),
        total_discount=Sum('discount'),
    )

    total_spent = stats['total_spent'] or 0
    average_order = stats['average_order'] or 0
    orders_count = stats['orders_count'] or 0
    total_discount = stats['total_discount'] or 0

    # Счётчик избранного (для карточки в профиле)
    favorites_count = Favorite.objects.filter(user=request.user).count()

    context = {
        'total_spent': total_spent,
        'average_order': average_order,
        'orders_count': orders_count,
        'total_discount': total_discount,
        'favorites_count': favorites_count,  # <-- важно: теперь цифра будет актуальной
    }
    return render(request, 'accounts/profile.html', context)
# @login_required
# def profile_view(request):
#     # 1. Статистика по заказам (ваш существующий код)
#     stats = request.user.user_orders.aggregate(
#         total_spent=Sum('total_price'),
#         average_order=Avg('total_price'),
#         orders_count=Count('id'),
#         total_discount=Sum('discount')
#     )
    
#     total_spent = stats['total_spent'] or 0
#     average_order = stats['average_order'] or 0
#     orders_count = stats['orders_count'] or 0
#     total_discount = stats['total_discount'] or 0

#     # 2. НОВАЯ ЛОГИКА: Получаем избранные товары
#     # select_related('product') нужен для оптимизации запросов (чтобы не делать N+1 запросов к БД)
#     favorites = Favorite.objects.filter(user=request.user).select_related('product')
#     favorites_count = favorites.count()

#     # 3. Формируем итоговый контекст
#     context = {
#         # Данные по заказам
#         'total_spent': total_spent,
#         'average_order': average_order,
#         'orders_count': orders_count,
#         'total_discount': total_discount,
        
#         # Данные по избранному (новые переменные)
#         'favorites': favorites,
#         'favorites_count': favorites_count,
#     }
    
#     return render(request, 'accounts/profile.html', context)

# @login_required
# def profile_view(request):
#     stats = request.user.user_orders.aggregate(
#         total_spent=Sum('total_price'),
#         average_order=Avg('total_price'),
#         orders_count=Count('id'),
#         total_discount=Sum('discount')  # <--- ДОБАВЬ ЭТУ СТРОКУ (имя поля должно совпадать с моделью)
#     )
    
#     # Теперь этот код сработает безопасно
#     total_spent = stats['total_spent'] or 0
#     average_order = stats['average_order'] or 0
#     orders_count = stats['orders_count'] or 0
#     total_discount = stats['total_discount'] or 0  # <--- Теперь ключ существует

#     context = {
#         'total_spent': total_spent,
#         'average_order': average_order,
#         'orders_count': orders_count,
#         'total_discount': total_discount,  # <--- Передаем в шаблон
#     }
#     return render(request, 'accounts/profile.html', context)

    # # Агрегируем суммы скидок и исходные суммы
    # stats = request.user.user_orders.aggregate(
    #     total_discount=Sum('discount_amount'),
    #     total_original=Sum('original_price')
    # )

    total_discount = stats['total_discount'] or 0
    total_original = stats['total_original'] or 0

    # Считаем процент: (Сумма скидок / Исходная сумма) * 100
    # Защита от деления на ноль, если заказов нет или original_price = 0
    if total_original > 0:
        average_discount_percent = (total_discount / total_original) * 100
    else:
        average_discount_percent = 0

    context = {
        # ... другие переменные ...
        'average_discount_percent': average_discount_percent,
    }

    # Средний чек
    if total_orders > 0:
        average_check = total_spent / total_orders
    else:
        average_check = 0

    # Добавляем average_check в контекст!
    context = {
        'user': request.user,
        'total_orders': total_orders,
        'total_spent': total_spent,
        'favorite_count': favorite_count,
        'orders': orders,
        'average_check': average_check,
        'average_discount_percent': average_discount_percent,
    }
    return render(request, 'accounts/profile.html', context)

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('products:home')
    else:
        # Исправляем здесь: создаем CustomUserCreationForm, а не UserCreationForm
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлён!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = UserEditForm(instance=request.user)
    context = {'form': form}
    return render(request, 'accounts/edit_profile.html', context)




@login_required
def settings_view(request):
    return render(request, 'accounts/settings.html')

@login_required
def orders_view(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')  # Исправлено: order_by → order_by
    return render(request, 'accounts/orders.html', {'orders': orders})

@login_required
def wishlist_view(request):
    wishlist_items = WishlistItem.objects.filter(user=request.user)
    return render(request, 'accounts/wishlist.html', {'wishlist_items': wishlist_items})

@login_required
def addresses_view(request):
    addresses = Address.objects.filter(user=request.user)
    return render(request, 'accounts/addresses.html', {'addresses': addresses})

# @login_required
# @require_POST
# def delete_card(request, card_id):
#     try:
#         # Удаляем только карту текущего пользователя
#         card = PaymentMethod.objects.get(id=card_id, user=request.user)
#         card.delete()
#         return JsonResponse({'status': 'ok'})
#     except PaymentMethod.DoesNotExist:
#         return JsonResponse({'status': 'error', 'message': 'Карта не найдена или не принадлежит вам'}, status=404)
    
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
    
# from favorites.models import Favorite


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

   