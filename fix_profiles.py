import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'techstore.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import Profile

User = get_user_model()

count = 0
for user in User.objects.all():
    profile, created = Profile.objects.get_or_create(user=user)
    if created:
        count += 1

print(f"Готово! Создано профилей для {count} пользователей.")