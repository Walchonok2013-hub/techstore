from django.urls import path
from . import views
app_name = 'cart'

urlpatterns = [
    # Основные маршруты корзины
    path('', views.cart_detail, name='detail'),
    path('add/<int:product_id>/', views.cart_add, name='add'),
  
    path('remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('ajax/', views.cart_ajax, name='cart_ajax'),
    path('remove_item/<int:product_id>/', views.cart_remove_item, name='cart_remove_item'),
    # path('remove-item/<int:product_id>/', views.cart_remove_item, name='remove_item'), 
]