from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('create/', views.order_create, name='order_create'),
    path('created/<int:order_id>/', views.order_created, name='order_created'),
    path('admin/order/<int:order_id>/', views.admin_order_detail, name='admin_order_detail'),
    path('payment/', views.payment_view, name='payment'),
    path('order/confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('products/', views.product_list, name='product_list'),
    path('payment/form/', views.payment_form_view, name='payment_form'), 
    path('my-orders/', views.my_orders, name='my_orders'),
    path('create/', views.create_order_view, name='create'),
    
   
     # приём данных и перенаправление
      # отображение формы оплаты
        
    
]