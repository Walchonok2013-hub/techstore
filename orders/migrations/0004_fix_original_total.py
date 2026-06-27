

from django.db import migrations

def fill_original_total(apps, schema_editor):
    Order = apps.get_model('orders', 'Order')
    
    # Берём ВСЕ заказы — так мы гарантированно исправим и 0, и NULL, и любые расхождения
    qs = Order.objects.all()
    
    count = 0
    for order in qs:
        order.original_total = order.total_price
        order.save(update_fields=['original_total'])
        count += 1
    
    print(f"[Migration] Fixed original_total for {count} orders.")

def reverse_fill(apps, schema_editor):
    # При откате миграции ничего не делаем — это безопасно
    pass

class Migration(migrations.Migration):
    # Указываем зависимость от ПРЕДЫДУЩЕЙ миграции (обычно это 0003_...)
    dependencies = [
        ('orders', '0003_fill_original_total'),
    ]

    operations = [
        migrations.RunPython(fill_original_total, reverse_fill),
    ]
