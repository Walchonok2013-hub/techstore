import logging
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from products.models import Product
from .cart import Cart
from django.contrib.auth.decorators import login_required
from .forms import CartAddProductForm
from decimal import Decimal, InvalidOperation
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages 
from decimal import Decimal
from django.template.exceptions import TemplateDoesNotExist
from django.http import HttpResponseRedirect
from django.http import HttpResponseRedirect
from django.urls import reverse

logger = logging.getLogger(__name__)

@require_POST
def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = Cart(request)
    # quantity=1, update_quantity=False — стандартное добавление
    cart.add(product=product, quantity=1, update_quantity=False)
    return redirect('cart:cart_detail')




def cart_remove(request, product_id):
    """Удаление товара из корзины"""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    # Для AJAX‑запросов возвращаем JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': 'Товар удалён из корзины',
            'total_items': len(cart),
            'total_price': str(cart.get_total_price())
        })
    return redirect('cart:cart_detail')

def cart_detail(request):
    """Отображение содержимого корзины"""
    cart = Cart(request)
    cart_items = []
    total_price = Decimal('0')
    items_count = 0

    # Проходимся по внутреннему словарю корзины
    for product_id, item_data in cart.cart.items():
        if not isinstance(item_data, dict):
            continue

        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            continue  # пропускаем товары, которых уже нет в БД

        try:
            price = Decimal(str(item_data.get('price', '0')))
            orig_price = Decimal(str(item_data.get('original_price', '0')))
            qty = int(item_data.get('quantity', 0))
            if qty < 0:
                qty = 0
        except (ValueError, InvalidOperation, TypeError):
            continue

        total_item_price = price * qty
        items_count += qty
        total_price += total_item_price

        cart_items.append({
            'product': product,
            'quantity': qty,
            'price': price,
            'original_price': orig_price,
            'total_price': total_item_price,
        })

    if items_count == 0:
        return redirect('products:catalog')

    return render(request, 'cart/detail.html', {
        'cart_items': cart_items,
        'total_items': items_count,
        'total_price': total_price,
    })

@csrf_exempt
def cart_ajax(request):
    """Возвращает данные корзины в формате JSON для AJAX‑обновлений"""
    cart = Cart(request)
    total_items = 0
    total_price = Decimal('0')
    items_data = []

    # Итерируемся по внутреннему словарю cart.cart, а не по самому объекту cart
    for product_id, item_data in cart.cart.items():
        if not isinstance(item_data, dict):
            continue

        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            continue

        try:
            price = Decimal(str(item_data.get('price', '0')))
            orig_price = Decimal(str(item_data.get('original_price', '0')))
            qty = int(item_data.get('quantity', 0))
            total_item_price = price * qty
        except (ValueError, InvalidOperation, TypeError):
            continue

        total_items += qty
        total_price += total_item_price

        items_data.append({
            'product_id': product.id,
            'name': product.name,
            'quantity': qty,
            'price': str(price),
            'total_price': str(total_item_price),
        })

    data = {
        'items_count': total_items,
        'total_price': str(total_price),
        'items': items_data,
        'html': f'<span>{total_items} товар(ов) — {total_price} руб.</span>'
    }
    return JsonResponse(data)  


def cart_remove_item(request, product_id):
    """
    Уменьшает количество товара в корзине на N штук.
    Если quantity <= 0 — удаляет товар полностью.
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)

    # Получаем желаемое уменьшение количества (по умолчанию 1)
    try:
        quantity_to_remove = int(request.POST.get('quantity', 1))
        if quantity_to_remove < 1:
            quantity_to_remove = 1
    except (ValueError, TypeError):
        quantity_to_remove = 1

    product_id_str = str(product_id)
    current_item = cart.cart.get(product_id_str)

    if not current_item:
        # Товара нет в корзине — можно вернуть ошибку или просто редирект
        messages.warning(request, 'Товар не найден в корзине')
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': 'Товар не найден в корзине',
                'total_items': len(cart),
                'total_price': str(cart.get_total_price()),
            })
        return redirect('cart:cart_detail')

    current_qty = current_item.get('quantity', 0)
    new_qty = max(0, current_qty - quantity_to_remove)

    if new_qty == 0:
        # Удаляем товар полностью
        cart.remove(product)
        msg = 'Товар удалён из корзины'
    else:
        # Обновляем количество
        cart.add(product=product, quantity=new_qty, update_quantity=True)
        msg = f'Количество товара уменьшено до {new_qty}'

    messages.info(request, msg)

    # AJAX-ответ
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': msg,
            'total_items': len(cart),
            'total_price': str(cart.get_total_price()),
        })

    return redirect('cart:cart_detail')       