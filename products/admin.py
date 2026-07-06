from django.contrib import admin
from .models import Category, Product, Promotion

@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('name', 'discount_percent', 'applies_to_category', 'is_active', 'expires_at')
    list_filter = ('is_active', 'applies_to_category')
    search_fields = ('name',)


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

