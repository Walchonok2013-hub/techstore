
from django.contrib import admin
from .models import Product, Category
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}  # slug заполняется автоматически из названия
    search_fields = ('name',)
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'available')
    list_filter = ('category', 'available', 'is_popular')
    search_fields = ('name',)

