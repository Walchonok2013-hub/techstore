
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .forms import UserEditForm
from .models import Order, WishlistItem, Address
from django.contrib.auth import views as auth_views
from techstore import settings
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .models import PaymentMethod
 

from .forms import AddCardForm


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
    # Проверяем, что карта принадлежит текущему пользователю
    card = get_object_or_404(PaymentMethod, pk=pk, user=request.user)
    if request.method == 'POST':
        card.delete()
        return redirect('cards_list')
    # Если зашли не через POST (например, по прямой ссылке), просто возвращаем в список
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
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}!')
            return redirect('products:home')
        else:
            messages.error(request, 'Ошибка в форме входа')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    username = request.user.username
    logout(request)
    messages.info(request, f'{username}, вы успешно вышли из системы')
    return redirect('main:index')
@login_required
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
# @login_required
# def payment_methods_view(request):
#     # ВАЖНО: .filter(user=request.user)
#     payment_methods = PaymentMethod.objects.filter(user=request.user)
    
#     context = {
#         'payment_methods': payment_methods,
        
        
#     }
#     return render(request, 'accounts/payment_methods.html', context)
@login_required
def profile_view(request):
    context = {'user': request.user}
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

@login_required
@require_POST
def delete_card(request, card_id):
    try:
        # Удаляем только карту текущего пользователя
        card = PaymentMethod.objects.get(id=card_id, user=request.user)
        card.delete()
        return JsonResponse({'status': 'ok'})
    except PaymentMethod.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Карта не найдена или не принадлежит вам'}, status=404)
    
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