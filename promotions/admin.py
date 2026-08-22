from django.contrib import admin
from .models import Promotion

@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('name', 'discount_percent', 'applies_to_category', 'is_active', 'expires_at')
    list_filter = ('is_active', 'applies_to_category')
    search_fields = ('name',)
    def __str__(self):
        return f"{self.name} ({self.discount_percent}%)"