
from django import template
from cart.models import Cart, CartItem

register = template.Library()

@register.simple_tag(takes_context=True)
def user_cart_count(context):
    request = context['request']
    user = request.user

    if user.is_authenticated:
        try:
            cart = Cart.objects.get(user=user, ordered=False)
            return cart.get_total_quantity()
        except Cart.DoesNotExist:
            return 0
    else:
        # Для анонимных пользователей — берём из сессии
        session_key = request.session.session_key
        if session_key:
            cart_items = CartItem.objects.filter(session_key=session_key, cart__ordered=False)
            return sum(item.quantity for item in cart_items)
        return 0