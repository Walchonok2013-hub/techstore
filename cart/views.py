
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
@csrf_protect
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)

    if form.is_valid():
        cd = form.cleaned_data
        try:
            quantity = int(cd['quantity'])  # Приводим к int
            if quantity < 1:
                raise ValueError("Количество должно быть положительным")
        except (ValueError, TypeError):
            # Обрабатываем ошибку — например, возвращаем сообщение пользователю
            messages.error(request, "Некорректное количество товара")
            return redirect('cart:detail')

        update_quantity = cd['update']
        cart.add(product=product, quantity=quantity, update_quantity=update_quantity)
        return redirect('cart:detail')
    else:
        # Обработка ошибок формы
        messages.error(request, "Ошибка в форме")
        #return redirect('products:product_detail', id=product_id)
        return redirect('products:product_detail', slug=product.slug)
# @require_POST
# @csrf_protect
# def cart_add(request, product_id):
#     """Добавление товара в корзину"""
#     cart = Cart(request)
#     product = get_object_or_404(Product, id=product_id)
#     form = CartAddProductForm(request.POST)

#     if form.is_valid():
#         cd = form.cleaned_data
#         quantity = cd['quantity']
#         update_quantity = cd['update']
#         cart.add(product=product, quantity=quantity, update_quantity=update_quantity)
#         # Для AJAX‑запросов возвращаем JSON
#         if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#             return JsonResponse({
#                 'success': True,
#                 'message': 'Товар добавлен в корзину',
#                 'total_items': len(cart),
#                 'total_price': str(cart.get_total_price())
#             })
#     else:
#         # Возвращаем ошибки формы для AJAX
#         if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#             return JsonResponse({
#                 'success': False,
#                 'errors': form.errors
#             }, status=400)

#     return redirect('cart:cart_detail')

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

# def cart_remove_item(request, product_id):
#     cart = Cart(request)
#     product = Product.objects.get(id=product_id)
#     quantity = int(request.POST.get('quantity', 1))

#     # Получаем текущее количество
#     current_item = cart.cart.get(str(product_id))
#     if current_item and current_item['quantity'] > quantity:
#         # Уменьшаем количество на указанное значение
#         new_quantity = current_item['quantity'] - quantity
#         cart.add(product=product, quantity=new_quantity, update_quantity=True)
#     else:
#         # Удаляем товар полностью
#         cart.remove(product)

#     messages.info(request, 'Количество товара изменено')
#     return redirect('cart:cart_detail')

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

    return redirect('cart:detail')
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
# def cart_detail(request):
#     cart = Cart(request)
#     try:
#         cart_items = list(cart)  # итерация через __iter__
#         total_items = len(cart)   # вызов __len__
#         total_price = cart.get_total_price()
#     except (TypeError, ValueError) as e:
#         print(f"Ошибка обработки данных корзины: {e}")
#         cart_items = []
#         total_items = 0
#         total_price = Decimal('0')
#     except Exception as e:
#         print(f"Неожиданная ошибка при обработке корзины: {e}")
#         cart_items = []
#         total_items = 0
#         total_price = Decimal('0')

    # Дополнительная проверка: убедитесь, что шаблон существует
    # try:
    #     return render(request, 'cart/detail.html', {
    #         'cart_items': cart_items,
    #         'total_items': total_items,
    #         'total_price': total_price
    #     })
    # except TemplateDoesNotExist:
    #     # Если шаблон не найден, показываем простое сообщение
    #     error_message = (
    #         "Шаблон корзины не найден.<br>"
    #         "Проверьте:<br>"
    #         "&bull; Существует ли файл cart/templates/cart/detail.html<br>"
    #         "&bull; Правильно ли настроены TEMPLATES в settings.py<br>"
    #         "&bull; Добавлено ли приложение 'cart' в INSTALLED_APPS"
    #     )
    #     return HttpResponse(error_message)
# def cart_detail(request):
#     cart = Cart(request)
#     try:
#         cart_items = list(cart)  # итерация через __iter__
#         total_items = len(cart)   # вызов __len__
#         total_price = cart.get_total_price()
#     except (TypeError, ValueError) as e:
#         print(f"Ошибка обработки данных корзины: {e}")
#         cart_items = []
#         total_items = 0
#         total_price = Decimal('0')
#     except Exception as e:
#         print(f"Неожиданная ошибка при обработке корзины: {e}")
#         cart_items = []
#         total_items = 0
#         total_price = Decimal('0')

#     return render(request, 'cart/detail.html', {
#         'cart_items': cart_items,
#         'total_items': total_items,
#         'total_price': total_price
#     })

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