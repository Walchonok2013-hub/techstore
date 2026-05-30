
# from django.urls import path
# from . import views

# app_name = 'products'

# urlpatterns = [
#     path('', views.home_page, name='home'),
#     path('catalog/', views.catalog, name='catalog'),
#     path('search/', views.search, name='search'),
#     path('category/<slug:slug>/', views.category_detail, name='category_detail'),
#     path('<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),
#     path('list/', views.product_list, name='product_list'),
#     path('cart/', views.cart_detail, name='cart_detail'),
#     path('delivery/', views.delivery, name='delivery'),
#     path('contacts/', views.contacts, name='contacts'),
#     path('about/', views.about, name='about'),
#     path('product/<int:product_id>/<slug:slug>/', views.product_detail, name='product_detail'),
    
# ]

from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # path('', views.home, name='home'),
    path('', views.home_page, name='home'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('products/', views.product_list, name='product_list'),
    path('<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),
    path('catalog/', views.catalog, name='catalog'),  # этот маршрут должен быть
    path('search/', views.search, name='search'),
    #path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('product/<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),
    path('list/', views.product_list, name='product_list'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('delivery/', views.delivery, name='delivery'),
    path('contacts/', views.contacts, name='contacts'),
    path('about/', views.about, name='about'),
    #path('<int:product_id>/', views.product_detail, name='product_detail')
    
]

