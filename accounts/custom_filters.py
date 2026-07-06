
from django import template

register = template.Library()

@register.filter
def add_spaces(value):
    if value is None:
        return "0"
    # Форматируем число и заменяем запятую на пробел
    return f"{int(value):,}".replace(",", " ")