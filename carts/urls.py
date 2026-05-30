
from django.urls import path
from . import views

urlpatterns = [
    path('ajax/', views.cart_ajax, name='cart_ajax'),
    # ... остальные URL вашего приложения корзины
]