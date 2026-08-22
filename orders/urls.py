
from django.urls import path
from . import views

app_name = 'orders'


urlpatterns = [
    path('create/', views.order_create, name='order_create'),
    path('<int:order_id>/', views.order_detail, name='order_detail'),
    path('created/<int:order_id>/', views.order_created, name='order_created'),
    path('admin/order/<int:order_id>/', views.admin_order_detail, name='admin_order_detail'),
    path('confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('cancel/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('products/', views.product_list, name='product_list'),
    path('<int:order_id>/detail/', views.order_detail_user, name='order_detail_user'),
    path('my_orders/', views.my_orders, name='my_orders'),
    

    path('payment/choice/<int:order_id>/', views.payment_choice, name='payment_choice'),
    path('payment_card/<int:order_id>/', views.payment_card, name='payment_card'),
    path('payment-success/<int:order_id>/', views.payment_success, name='payment_success'),

]