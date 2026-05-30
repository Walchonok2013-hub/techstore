"""
URL configuration for techstore project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

# from django.urls import path, include
from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView  # правильный импорт RedirectView
from user import views as user_views  # импорт представлений из приложения user
from django.conf import settings
from django.conf.urls.static import static
from user.views import *


    
urlpatterns = [
    path('admin/', admin.site.urls),
    path('products/', include('products.urls', namespace='products')),
    path('cart/', include('cart.urls', namespace='cart')),
    path('orders/', include('orders.urls', namespace='orders')),
    path('user/', include('user.urls')),
    path('myapp/', include('myapp.urls')),
    path('accounts/', include('accounts.urls')),
    path('shop/', include('shop.urls')), 
    
    path('main/', include('main.urls', namespace='main')),
    path('', RedirectView.as_view(url='/products/'), name='home'),
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Только в режиме разработки (DEBUG = True)




