from django.shortcuts import render
from cart.cart import Cart

def cart_ajax(request):
    cart = Cart(request)
    return render(request, 'carts/includes/included_cart.html', {'cart': cart})