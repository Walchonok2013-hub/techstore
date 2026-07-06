from .models import Promotion
from django.utils import timezone

def get_active_promotion_for_category(category):
    """
    Возвращает активную акцию для категории с МАКСИМАЛЬНОЙ скидкой.
    """
    if not category:
        return None

    return Promotion.objects.filter(
        applies_to_category=category,
        is_active=True,
        expires_at__gte=timezone.now()  # <-- исправлено: два подчёркивания
    ).order_by('-discount_percent').first()