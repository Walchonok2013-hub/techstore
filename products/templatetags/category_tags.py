from django import template
from products.models import Category

register = template.Library()  # ОБЯЗАТЕЛЬНО: регистрирует библиотеку тегов

@register.simple_tag
def tag_categories():
    """Возвращает все активные категории"""
    return Category.objects.filter(is_active=True)



