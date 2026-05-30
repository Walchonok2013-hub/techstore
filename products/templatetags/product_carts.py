
from django import template
from cart.models import CartItem 

register = template.Library()

@register.simple_tag
def get_user_cart_items(user):
    try:
        cart = user.cart
        return cart.items.all()
    except:
        return []