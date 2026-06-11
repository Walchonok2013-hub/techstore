import django.db.models.deletion
import django.utils.timezone

from django.db import migrations, models
from django.conf import settings



class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0001_initial'),  # укажите предыдущую миграцию
    ]

    operations = [
        # Добавляем поле user с дефолтным пользователем
        migrations.AddField(
            model_name='paymentmethod',
            name='user',
            field=models.ForeignKey(
                default=1,
                on_delete=models.CASCADE,
                related_name='payment_methods',
                to=settings.AUTH_USER_MODEL,
            ),
            preserve_default=False,
        ),
        # Удаляем устаревшие поля
        migrations.RemoveField(
            model_name='paymentmethod',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='paymentmethod',
            name='description',
        ),
        migrations.RemoveField(
            model_name='paymentmethod',
            name='fee_percent',
        ),
        migrations.RemoveField(
            model_name='paymentmethod',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='paymentmethod',
            name='name',
        ),
        # Добавляем новые поля
        migrations.AddField(
            model_name='paymentmethod',
            name='card_type',
            field=models.CharField(default='visa', max_length=20),
        ),
        migrations.AddField(
            model_name='paymentmethod',
            name='is_default',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='paymentmethod',
            name='last_digits',
            field=models.CharField(default='0000', max_length=4),  # Исправлено: строка вместо числа
            preserve_default=False,
        ),
    ]