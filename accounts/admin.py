
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import Group, User

# --- НАСТРОЙКА ГРУПП (Groups -> Группы) ---
# 1. Сначала снимаем стандартную регистрацию, иначе будет ошибка AlreadyRegistered
admin.site.unregister(Group)

# 2. Регистрируем заново с нашим классом админки
admin.site.register(Group, GroupAdmin)

# 3. Меняем название именно у МОДЕЛИ (Group), а не у класса админки
Group._meta.verbose_name = 'Группа'
Group._meta.verbose_name_plural = 'Группы'


# --- НАСТРОЙКА ПОЛЬЗОВАТЕЛЕЙ (Users -> Пользователи) ---
# 1. Снимаем стандартную регистрацию
admin.site.unregister(User)

# 2. Регистрируем заново
admin.site.register(User, UserAdmin)

# 3. Меняем название у МОДЕЛИ (User)
User._meta.verbose_name = 'Пользователь'
User._meta.verbose_name_plural = 'Пользователи'
