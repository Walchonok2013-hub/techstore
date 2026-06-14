from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'user'

urlpatterns = [

    # Регистрация пользователя
    path('register/', views.register, name='register'),

    # Аутентификация
    path('login/', auth_views.LoginView.as_view(template_name='user/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Профиль пользователя
    path('profile/', views.profile, name='profile'),

    # Сброс пароля
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='user/password_reset/password_reset.html'
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='user/password_reset/password_reset_done.html'
    ), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='user/password_reset/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='user/password_reset/password_reset_complete.html'
    ), name='password_reset_complete'),
]
  