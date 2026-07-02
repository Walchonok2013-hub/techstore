from django.contrib import admin
from .models import Order, OrderItem, Payment

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'get_display_total', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'id')
    
    # ЭТА СТРОКА позволяет менять статус прямо в списке (кликаешь по ячейке и выбираешь)
    list_editable = ('status',) 
    
    # ЭТА СТРОКА говорит Django: "ссылкой на полное редактирование делай только ID"
    # (иначе при клике на статус он будет пытаться открыть редактирование заказа, а не менять значение)
    list_display_links = ('id',) 

    def get_display_total(self, obj):
        # Используем Decimal напрямую, f-string сам его красиво отформатирует
        return f"{obj.total_price} ₽"
    
    get_display_total.short_description = 'Итого'

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price', 'get_cost_display')
    list_filter = ('order',)

    # Опционально: тоже покажем расчетную стоимость позиции в админке
    def get_cost_display(self, obj):
        return f"{obj.price * obj.quantity} ₽"
    
    get_cost_display.short_description = 'Стоимость позиции'

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'payment_method', 'amount', 'is_completed', 'completed_at')
    list_filter = ('payment_method', 'is_completed')





