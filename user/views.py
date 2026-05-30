from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


def home(request):
    context = {}
    return render(request, 'user/home.html', context)


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # автоматический вход после регистрации
            return redirect('products:product_list')  # перенаправление после успешной регистрации
    else:
        form = UserCreationForm()
    return render(request, 'user/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Добро пожаловать, {username}!')
                return redirect('main:index')  # перенаправление на главную
            else:
                messages.error(request, 'Неверные учётные данные')
        else:
            messages.error(request, 'Ошибка в форме входа')
    else:
        form = AuthenticationForm()
    return render(request, 'user/login.html', {'form': form})


@login_required
def profile(request):
    context = {'user': request.user}
    return render(request, 'user/profile.html', context)


def logout_view(request):
    username = request.user.username
    logout(request)
    messages.info(request, f'{username}, вы успешно вышли из системы')
    return redirect('main:index')