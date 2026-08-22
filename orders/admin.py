
from django.contrib import admin
from .models import Order, OrderItem, Payment


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    
    # В readonly_fields кладем только реальные поля модели.
    # Методы модели (discount_amount, get_cost) сюда НЕ добавляем.
    readonly_fields = ('product', 'quantity', 'final_price', 'original_price')
    
    # В fields тоже только реальные поля.
    # Мы НЕ можем редактировать discount_amount или get_cost — это вычисляемые значения.
    fields = ('product', 'quantity', 'final_price', 'original_price')

    # Если хочешь видеть скидку и итоговую стоимость прямо в таблице инлайна,
    # добавь их в list_display (но это для TabularInline работает не всегда так, как хочется).
    # Лучше показывать это в админке самого заказа или в шаблоне.


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total_price_display', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'phone', 'email', 'id')

    inlines = [OrderItemInline]
    readonly_fields = ('created_at', 'original_total', 'discount', 'total_price')

    def total_price_display(self, obj):
        return f"{obj.total_price} ₽"
    
    total_price_display.short_description = 'Итого'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'final_price', 'cost_display')
    list_filter = ('order__status', 'order')

    @admin.display(description='Стоимость')
    def cost_display(self, obj):
        return f"{obj.final_price * obj.quantity} ₽"


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'payment_method', 'amount', 'is_completed', 'completed_at')
    list_filter = ('payment_method', 'is_completed')
    search_fields = ('order__id',)




