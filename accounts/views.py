
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .forms import UserEditForm
from .models import Order, WishlistItem, Address

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}!')
            return redirect('home:index')
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

def payment_methods_view(request):
    payment_methods = [
        {'name': 'Банковская карта', 'icon': 'credit-card'},
        {'name': 'Электронный кошелёк', 'icon': 'wallet'},
        {'name': 'Наличные при получении', 'icon': 'cash'},
    ]
    context = {
        'payment_methods': payment_methods,
        'title': 'Способы оплаты'
    }
    return render(request, 'accounts/payment_methods.html', context)

@login_required
def profile_view(request):
    context = {'user': request.user}
    return render(request, 'accounts/profile.html', context)

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('main:index')
    else:
        form = UserCreationForm()
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
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Сохраняем сессию
            messages.success(request, 'Пароль успешно изменён!')
            return redirect('accounts:profile')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/change_password.html', {'form': form})

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

