
from django.urls import path
from . import views

app_name = 'myapp'

urlpatterns = [
    path('', views.home, name='home'),
    path('info/', views.info, name='info'),
    path('info/delivery/', views.delivery, name='delivery'),
    path('info/contacts/', views.contacts, name='contacts'),
    path('info/about/', views.about, name='about'),
]