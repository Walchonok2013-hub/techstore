
from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    # Основные приложения
    
    path('cart/', include('cart.urls', namespace='cart')),
    path('user/', include('user.urls')),
    path('myapp/', include('myapp.urls')),
    path('accounts/', include('accounts.urls')),
    path('shop/', include('shop.urls')),
    path('main/', include('main.urls', namespace='main')),
    path('orders/', include('orders.urls', namespace='orders')),
    path('products/', include('products.urls')),
    
    # Главная страница
    path('', RedirectView.as_view(url='/products/'), name='home'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)




