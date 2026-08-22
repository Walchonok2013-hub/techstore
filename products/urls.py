from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.home_page, name='home'),
    path('search/', views.search_view, name='search'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('catalog/', views.catalog_view, name='catalog'),

    # Быстрая кнопка «В корзину» для каталога
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),

    path('contacts/', views.contacts, name='contacts'),
    path('about/', views.about, name='about'),
    path('products/toggle-favorite/', views.toggle_favorite, name='toggle_favorite'),

    # В самом конце — карточка товара
    path('<slug:slug>/', views.product_detail, name='product_detail'),
]

                                            

