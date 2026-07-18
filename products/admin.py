from django.contrib import admin
from .models import Category, Product




@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug','is_active')
    list_filter = ('is_active',)
    search_fields = ('name','slug')
    prepopulated_fields = {'slug': ('name',)}
    def __str__(self):
        return self.name  
      
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'available')
    list_filter = ('category', 'available', 'is_popular')
    search_fields = ('name',)

