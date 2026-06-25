from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    
    # 2. Админка и приложения
    path('admin/', admin.site.urls),
    path('cart/', include('cart.urls', namespace='cart')),
    path('accounts/', include('accounts.urls')),
    path('main/', include('main.urls', namespace='main')),
    path('orders/', include('orders.urls', namespace='orders')),
    
    # 3. ПРОДУКТЫ — ТОЛЬКО В САМОМ КОНЦЕ!
    path('', include('products.urls')),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Добавляем статику ТОЛЬКО если DEBUG=True
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)




