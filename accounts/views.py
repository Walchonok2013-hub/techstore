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
from django.contrib import messages
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from decimal import Decimal, ROUND_HALF_UP
from orders.models import Order
from django.shortcuts import render, redirect
# from .services import create_yookassa_payment_method 
import yookassa
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt




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
    favorites_count = Favorite.objects.filter(user=request.user).count()
    
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

@login_required
def create_address(request):
    if request.method == 'POST':
        title = request.POST.get('title', '')
        full_address = request.POST.get('full_address', '')
        phone = request.POST.get('phone', '')
        notes = request.POST.get('notes', '')
        is_default_raw = request.POST.get('is_default')
        is_default = (is_default_raw == 'on')

        # Если ставят «основной» — сначала снимаем флаг со всех остальных
        if is_default:
            Address.objects.filter(user=request.user).update(is_default=False)
        elif not Address.objects.filter(user=request.user).exists():
            # Если адресов вообще нет — первый автоматически станет основным
            is_default = True

        address = Address.objects.create(
            user=request.user,
            title=title,
            full_address=full_address,
            phone=phone,
            notes=notes,
            is_default=is_default,
        )

        messages.success(request, 'Адрес успешно добавлен.')
        return redirect('accounts:profile_addresses')

    # GET — показываем форму создания
    return render(request, 'accounts/addresses.html') 

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
    addresses = request.user.addresses.all().order_by('-is_default', 'title')
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
def create_yookassa_payment_for_card_binding(request):
    """
    Создаёт платёж в YooKassa с save_payment_method=True и суммой 0.00
    для привязки карты. Возвращает URL для редиректа.
    """
    try:
        payment = yookassa.Payment.create({
            "amount": {
                "value": "0.00",
                "currency": "RUB"
            },
            "confirmation": {
                # type=redirect: YooKassa покажет свою форму оплаты
                "type": "redirect",
                # return_url: куда вернуть пользователя после ввода карты
                "return_url": f"{settings.BASE_URL}/accounts/payment-methods/"
            },
            # save_payment_method=True: YooKassa сохранит способ оплаты и вернёт payment_method.id
            "save_payment_method": True,
            "capture": False,  # Не списывать деньги (т.к. сумма 0)
            "description": f"Привязка карты для пользователя {request.user.username}"
        })

        # payment.confirmation.type может быть 'redirect', тогда confirmation.url — это URL редиректа
        if payment.confirmation and payment.confirmation.type == "redirect":
            return JsonResponse({
                "url": payment.confirmation.confirmation_url,
                "payment_id": payment.id
            })
        else:
            return HttpResponseBadRequest("Некорректный тип подтверждения от YooKassa")

    except Exception as e:
        # В продакшене логируйте ошибку, а не возвращайте текст исключения
        return JsonResponse({"error": str(e)}, status=500)

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
    # Берем только способы оплаты текущего пользователя
    # Теперь здесь будут объекты с полями yookassa_payment_method_id, card_mask и т.д.
    payment_methods = PaymentMethod.objects.filter(user=request.user)
    
    context = {
        'payment_methods': payment_methods,
        'title': 'Способы оплаты'
    }
    return render(request, 'accounts/payment_methods.html', context)

@login_required
def payment_methods_add(request):
    if request.method == 'POST':
        # 1. Получаем payment_method_id и card_mask от YooKassa.
        # В реальном проекте это приходит через webhook или ответ API после виджета.
        # Для примера предположим, что мы получили их из POST (в реальности так не делают из соображений безопасности,
        # лучше использовать webhook или ответ JS виджета).
        
        yookassa_id = request.POST.get('yookassa_payment_method_id')
        card_mask = request.POST.get('card_mask')
        payment_type = request.POST.get('payment_type', 'card')

        if yookassa_id:
            # 2. Сохраняем ТОЛЬКО токен/ID в базу
            PaymentMethod.objects.create(
                user=request.user,
                yookassa_payment_method_id=yookassa_id,
                card_mask=card_mask,
                payment_type=payment_type,
                is_default=True # Можно сделать первой картой дефолтной
            )
            messages.success(request, 'Способ оплаты успешно сохранен!')
            return redirect('accounts:payment-methods') # Редирект на список, а не на себя
        else:
            messages.error(request, 'Не удалось получить данные от платежной системы.')
            return redirect('accounts:payment-methods-add')

    # GET запрос: просто показываем форму (или виджет YooKassa)
    return render(request, 'accounts/payment_methods_add.html')



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
    # Приводим к Decimal сразу, чтобы избежать ошибок при делении int/None
    total_spent_raw = stats['total_spent'] or Decimal('0')
    orders_count = stats['orders_count'] or 0
    total_discount_raw = stats['total_discount'] or Decimal('0')
    total_original_raw = stats['total_original'] or Decimal('0')

    # --- РАСЧЕТЫ С ОКРУГЛЕНИЕМ ---
    
    # 1. Средняя скидка в процентах: (Сумма скидок / Сумма исходных цен) * 100
    if total_original_raw > 0:
        avg_discount_raw = (total_discount_raw / total_original_raw) * 100
        # Округляем до 1 знака после запятой (банковское округление)
        average_discount_percent = avg_discount_raw.quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)
    else:
        average_discount_percent = Decimal('0.0')

    # 2. Средний чек: Потрачено / Количество заказов
    if orders_count > 0:
        avg_check_raw = total_spent_raw / orders_count
        # Округляем до 1 знака после запятой
        average_check = avg_check_raw.quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)
    else:
        average_check = Decimal('0.0')

    # Считаем избранное
    favorites_count = Favorite.objects.filter(user=request.user).count()

    context = {
        'user': request.user,
        'total_spent': total_spent_raw,       # Можно оставить raw или тоже округлить
        'orders_count': orders_count,
        'favorites_count': favorites_count,
        'average_discount_percent': average_discount_percent,
        'average_check': average_check,
    }

    return render(request, 'accounts/profile.html', context)



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
    
    qs = (
        request.user.user_favorites
        .select_related('product')
        .order_by('-id')        
    )

    paginator = Paginator(qs, 9) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'title': 'Избранное',
        'page_obj': page_obj,
        'wishlist_count': page_obj.paginator.count,
    }
    return render(request, 'accounts/favorites.html', context)




   