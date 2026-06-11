
from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.home_page, name='home'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('products/', views.product_list, name='product_list'),
    # path('<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),
    path('catalog/', views.catalog, name='catalog'),
    path('search/', views.search, name='search'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('delivery/', views.delivery, name='delivery'),
    path('contacts/', views.contacts, name='contacts'),
    path('about/', views.about, name='about'),
    path('toggle-favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('catalog/', views.catalog, name='catalog'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    
]


# from . import views


# from django.urls import path, include
# app_name = 'products'

# urlpatterns = [
#     # path('', views.home, name='home'),
#     path('', views.home_page, name='home'),
#     path('category/<slug:slug>/', views.category_detail, name='category_detail'),
#     path('products/', views.product_list, name='product_list'),
#     path('<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),
#     path('catalog/', views.catalog, name='catalog'),  # этот маршрут должен быть
#     path('search/', views.search, name='search'),
#     #path('category/<slug:slug>/', views.category_detail, name='category_detail'),
#     path('product/<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),
#     path('list/', views.product_list, name='product_list'),
#     path('cart/', views.cart_detail, name='cart_detail'),
#     path('delivery/', views.delivery, name='delivery'),
#     path('contacts/', views.contacts, name='contacts'),
#     path('about/', views.about, name='about'),
#     #path('<int:product_id>/', views.product_detail, name='product_detail')
#     path('toggle-favorite/', views.toggle_favorite, name='toggle_favorite'),
#     path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
#     path('products/', include('products.urls')),
      
   
# ]

