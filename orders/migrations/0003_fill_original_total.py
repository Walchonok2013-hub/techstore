
from django.db import migrations

def fill_original_total(apps, schema_editor):
    Order = apps.get_model('orders', 'Order')
    
    # Обновляем только те заказы, где original_total == 0
    # Это важно: новые заказы уже имеют правильное значение, их трогать не надо
    qs = Order.objects.filter(original_total=0)
    
    count = 0
    for order in qs:
        order.original_total = order.total_price + order.discount
        order.save(update_fields=['original_total'])
        count += 1
    
    print(f"[Migration] Updated original_total for {count} orders.")

def reverse_fill(apps, schema_editor):
    # При откате миграции (migrate назад) мы ничего не делаем.
    # Это безопасно, так как мы не удаляем данные, а только заполняем пустые.
    pass

class Migration(migrations.Migration):
    # Самое важное: указываем предыдущую миграцию, где появилось поле
    dependencies = [
        ('orders', '0002_order_original_total'),
    ]

    operations = [
        migrations.RunPython(fill_original_total, reverse_fill),
    ]