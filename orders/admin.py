from django.contrib import admin
from django.conf import settings
from .models import Order, OrderItem, Product

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'first_name', 'last_name',
                   'email', 'address', 'city', 'postal_code',
                   'created', 'updated', 'paid']
    list_filter = ['paid', 'created', 'updated']

    # Убрали 'status' из list_display и list_filter

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'price', 'quantity']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'in_stock', 'slug']
    list_filter = ['in_stock']  # Убрали 'created' из list_filter
    prepopulated_fields = {'slug': ('name',)}



