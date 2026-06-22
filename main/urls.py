from django.urls import path
from . import views

app_name = 'main'  # это и есть namespace

urlpatterns = [
    path('', views.index, name='home'),
    path('about/', views.about, name='about'),
    path('contacts/', views.contacts, name='contacts'),
    path('delivery/', views.delivery, name='delivery'),
    path('categories/', views.categories, name='categories'), 
    
]