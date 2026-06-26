from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('register/', views.register_view, name='register'),
    path('settings/', views.settings_view, name='settings'),

    # Заказы, избранное, адреса, способы оплаты
    path('orders/', views.orders_view, name='orders'),

    path('addresses/<int:pk>/delete/', views.delete_address, name='delete_address'),
    path('addresses/', views.profile_addresses, name='profile_addresses'),  # <-- только этот путь для списка
    path('addresses/create/', views.create_address, name='create_address'),  # <-- этот путь нужен для формы
    path('addresses/<int:address_id>/edit/', views.edit_address, name='edit_address'),
    path('payment-methods/', views.payment_methods_view, name='payment_methods'),
    path('change-password/', views.change_password_view, name='change_password'),

    path('payment-methods/<int:card_id>/delete/', views.delete_card, name='delete_card'),
    path('payment-methods/add/', views.payment_methods_add, name='payment-methods-add'),
    path('cards/', views.cards_list, name='cards_list'),
    path('cards/add/', views.add_card, name='add_card'),
    path('cards/<int:pk>/delete/', views.delete_card, name='delete_card'),

    path('favorites/<int:product_id>/toggle/', views.toggle_favorite_ajax, name='toggle_favorite'),
    path('favorites/', views.user_favorites, name='favorites'),

    # Сброс пароля
    path('password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='accounts/password_reset.html',
            email_template_name='accounts/password_reset_email.html',
            success_url='/accounts/password-reset/done/'
        ),
        name='password_reset'),
    path('password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='accounts/password_reset_done.html'
        ),
        name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='accounts/password_reset_confirm.html',
            success_url='/accounts/reset/done/'
        ),
        name='password_reset_confirm'),
    path('reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='accounts/password_reset_complete.html'
        ),
        name='password_reset_complete'),
]
    
    
    
