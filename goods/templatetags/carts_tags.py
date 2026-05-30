from django import template
from cart.models import CartItem
from django.contrib.auth.models import User

register = template.Library()

@register.simple_tag(takes_context=True)
def user_cart_count(context):
    """
    Возвращает количество товаров в корзине пользователя.
    Работает для авторизованных и неавторизованных пользователей.
    """
    request = context['request']

    if request.user.is_authenticated:
        # Для авторизованных пользователей — считаем CartItem
        return CartItem.objects.filter(user=request.user).count()
    else:
        # Для гостей — используем сессионную корзину
        from cart.cart import Cart
        cart = Cart(request)
        return len(cart)

@register.simple_tag(takes_context=True)
def user_cart_total(context):
    """
    Возвращает общую стоимость товаров в корзине.
    """
    request = context['request']

    if request.user.is_authenticated:
        # Для авторизованных: сумма по CartItem
        cart_items = CartItem.objects.filter(user=request.user)
        return sum(item.get_total_price() for item in cart_items)
    else:
        # Для гостей: сумма из сессионной корзины
        from cart.cart import Cart
        cart = Cart(request)
        return cart.get_total_price()

@register.inclusion_tag('products/includes/cart_info.html', takes_context=True)
def show_cart_info(context):
    """
    Рендерит HTML‑блок с информацией о корзине.
    Использует отдельный шаблон для гибкости.
    """
    request = context['request']
    count = user_cart_count(context)
    total = user_cart_total(context)

    return {
        'cart_count': count,
        'cart_total': total,
        'user_is_authenticated': request.user.is_authenticated
    }
