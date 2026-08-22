from cart.models import Cart, CartItem

def cart(request):
    """
    Добавляет в контекст данные о корзине текущего пользователя.
    """
    cart_data = {
        'cart_item_count': 0,
        'cart_total': 0,
    }

    if request.user.is_authenticated:
        try:
            from cart.models import Cart, CartItem
            cart = Cart.objects.get(user=request.user)
            cart_items = CartItem.objects.filter(cart=cart)
            cart_data['cart_item_count'] = sum(item.quantity for item in cart_items)
            cart_data['cart_total'] = sum(
                item.product.price * item.quantity for item in cart_items
            )
        except Cart.DoesNotExist:
            pass

    return cart_data