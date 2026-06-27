from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from products.models import Product
from .cart import Cart

from .forms import CartAddProductForm

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages 
from decimal import Decimal
from django.template.exceptions import TemplateDoesNotExist
from django.http import HttpResponse



@require_POST
def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})

    # Приводим ID к строке, чтобы избежать проблем с типами
    product_id_str = str(product_id)

    if product_id_str in cart:
        cart[product_id_str]['quantity'] += 1
    else:
        cart[product_id_str] = {
            'product_id': product_id,
            'name': product.name,
            'price': str(product.price),  # сохраняем как строку для JSON-совместимости сессии
            'quantity': 1,
        }

    # Обязательно помечаем сессию как изменённую
    request.session['cart'] = cart
    request.session.modified = True

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



def cart_remove_item(request, product_id):
    cart = Cart(request)

    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        messages.error(request, 'Товар не найден')
        return redirect('cart:cart_detail')

    quantity = int(request.POST.get('quantity', 1))

    # Безопасное получение элемента корзины
    current_item = cart.cart.get(str(product_id))

    if current_item:
        if current_item['quantity'] > quantity:
            new_quantity = current_item['quantity'] - quantity
            cart.add(product=product, quantity=new_quantity, update_quantity=True)
            messages.info(request, 'Количество товара уменьшено')
        else:
            cart.remove(product)
            messages.info(request, 'Товар удалён из корзины')
    else:
        messages.warning(request, 'Товар не найден в корзине')

    return redirect('cart:cart_detail')
def cart_detail(request):
    cart = Cart(request)
    try:
        cart_items = list(cart)
        total_items = len(cart)
        total_price = cart.get_total_price()
    except (TypeError, ValueError) as e:
        print(f"Ошибка обработки данных корзины: {e}")
        cart_items = []
        total_items = 0
        total_price = Decimal('0')
    except Exception as e:
        print(f"Неожиданная ошибка при обработке корзины: {e}")
        cart_items = []
        total_items = 0
        total_price = Decimal('0')

    return render(request, 'cart/detail.html', {
        'cart_items': cart_items,
        'total_items': total_items,
        'total_price': total_price
    })


@csrf_exempt  # или @csrf_protect, в зависимости от требований
def cart_ajax(request):
    """Возвращает данные корзины в формате JSON для AJAX‑обновлений"""
    cart = Cart(request)
    try:
        cart_items = list(cart)
        total_items = len(cart)
        total_price = cart.get_total_price()
        items_data = []

        for item in cart_items:
            items_data.append({
                'product_id': item['product'].id,
                'name': item['product'].name,
                'quantity': item['quantity'],
                'price': str(item['price']),
                'total_price': str(item['total_price'])
            })

        data = {
            'items_count': total_items,
            'total_price': str(total_price),
            'items': items_data,
            'html': f'<span>{total_items} товар(ов) — {total_price} руб.</span>'
        }
    except Exception as e:
        print(f"Ошибка при формировании AJAX‑данных корзины: {e}")
        data = {
            'items_count': 0,
            'total_price': '0',
            'items': [],
            'html': '<span>Корзина пуста</span>'
        }

    return JsonResponse(data)