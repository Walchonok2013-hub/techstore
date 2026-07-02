from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from .forms import OrderCreateForm
from .models import Order, OrderItem, Payment
from cart.models import Cart as CartModel  # Импортируем МОДЕЛЬ корзины, а не класс-обертку
import logging
from cart.cart import Cart
from django.db.models import Sum, F
from django.contrib import messages

logger = logging.getLogger(__name__)


@login_required
def payment_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    payment = getattr(order, 'payment', None)

    # Если платежа нет — не меняем статус
    if not payment:
        messages.warning(request, "Платеж не найден. Статус заказа не изменён.")
        return redirect('orders:my_orders')

    # Помечаем сам объект платежа как завершённый
    payment.is_completed = True
    payment.save()

    # ГЛАВНОЕ ИСПРАВЛЕНИЕ: проверяем метод оплаты
    # Замени 'cash' на то значение, которое у тебя в choices для «При получении»
    if payment.payment_method != 'cash':
        order.status = 'paid'
        order.save()
        messages.success(
            request,
            f"Оплата заказа #{order.id} успешно завершена! Способ: {payment.get_payment_method_display()}"
        )
    else:
        # Для наложенного платежа статус не меняем, показываем нейтральное сообщение
        messages.info(
            request,
            f"Данные заказа #{order.id} зафиксированы. Оплата будет произведена при получении."
        )

    return redirect('orders:my_orders')

# @login_required
# def payment_success(request, order_id):
#     """Имитация успешного завершения платежа и финальная фиксация данных"""
#     order = get_object_or_404(Order, id=order_id, user=request.user)
    
#     # 1. Пытаемся найти связанный платеж
#     payment = getattr(order, 'payment', None)
    
#     if payment:
#         # Если платеж существует, помечаем его как завершенный
#         payment.is_completed = True
#         payment.save()
        
#         # ВАЖНО: Обновляем статус заказа на основе метода оплаты из платежа
#         # Например, если платили картой, можно поставить статус 'paid', если СБП - 'completed'
#         order.status = 'paid' 
#         order.save()
        
#         messages.success(request, f"Оплата заказа #{order.id} успешно завершена! Способ: {payment.get_payment_method_display()}")
#     else:
#         # Если по какой-то причине платежа нет (редкий кейс), ставим статус вручную
#         order.status = 'paid'
#         order.save()
#         messages.success(request, f"Оплата заказа #{order.id} успешно завершена!")

#     return redirect('orders:my_orders')
@login_required
@transaction.atomic
def order_create(request):
    cart = Cart(request)

    if len(cart) == 0:
        messages.warning(request, "Ваша корзина пуста.")
        return redirect('cart:cart_detail')

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            # 1. Создаем черновик заказа
            order = form.save(commit=False)
            order.user = request.user if request.user.is_authenticated else None
            order.status = 'pending'
            order.save()  # Сохраняем, чтобы получить order.id для связи с позициями

            # 2. Создаем все позиции заказа (OrderItem)
            for item in cart:
                product = item['product']
                qty = item['quantity']
                price = item['price']

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=qty,
                    price=price,
                    # total_price=price * qty  # Раскомментируй, если в модели OrderItem есть это поле
                )

            # 3. ГЛАВНОЕ ИСПРАВЛЕНИЕ: Считаем итоговую сумму через БД, а не циклом в Python
            # Это гарантирует, что total_price всегда равен сумме позиций
            total_sum = order.items.aggregate(total=Sum(F('price') * F('quantity')))['total']
            
            # Если заказ вдруг пустой (защита от None), ставим 0
            final_total = total_sum if total_sum is not None else 0
            
            order.total_price = final_total
            order.original_total = final_total
            order.save(update_fields=['total_price', 'original_total'])

            request.session['pending_order_id'] = order.id

            messages.success(request, f"Заказ #{order.id} создан. Выберите способ оплаты.")
            return redirect('orders:payment_choice', order.id)
    else:
        form = OrderCreateForm()

    return render(request, 'orders/create.html', {'form': form, 'cart': cart})
  




# @login_required

# def order_create(request):
#     cart = Cart(request)
    
#     if not cart:
#         messages.warning(request, 'Ваша корзина пуста.')
#         return redirect('cart:cart_detail')

#     if request.method == 'POST':
#         form = OrderCreateForm(request.POST)
#         if form.is_valid():
#             try:
#                 # 1. Создаем черновик заказа
#                 order = form.save(commit=False)
#                 order.user = request.user  # request.user всегда есть из-за @login_required
                
#                 # 2. Сохраняем заказ, чтобы получить ID
#                 order.save() 
                
#                 # 3. Считаем сумму и создаем позиции
#                 total_cost = 0
                
#                 for item in cart:
#                     product = item.get('product')
#                     if product:
#                         price = item['price']
#                         qty = item['quantity']
#                         item_total = price * qty
#                         total_cost += item_total
                        
#                         OrderItem.objects.create(
#                             order=order,
#                             product=product,
#                             price=price,
#                             quantity=qty
#                         )
#                     else:
#                         # Товар удален — удаляем из корзины
#                         cart.remove(str(item.get('product_id', '')))
#                         messages.warning(request, f'Товар был удален из каталога и исключен из заказа.')
                
#                 # 4. Обновляем итоговые поля заказа
#                 order.original_total = total_cost
#                 order.total_price = total_cost
#                 order.save()  # Обновляем сумму
                
#                 # 5. Очищаем корзину ТОЛЬКО после успешного создания всех позиций
#                 cart.clear()
                
#                 # 6. Сообщение об успехе
#                 messages.success(request, f'Заказ #{order.id} успешно оформлен!')


#                 return redirect('orders:my_orders') 

#             except Exception as e:
#                 logger.error(f"Критическая ошибка при создании заказа: {e}")
#                 # Так как мы используем @transaction.atomic, заказ и позиции автоматически удалятся из БД
#                 messages.error(request, 'Произошла ошибка при оформлении заказа. Попробуйте позже.')
#                 return redirect('cart:cart_detail')
#         else:
#             messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
#     else:
#         form = OrderCreateForm()

#     return render(request, 'orders/create.html', {'form': form, 'cart': cart})

    
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'admin/orders/order/detail.html', {'order': order})



def order_created(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'orders/created.html', {'order': order, 'order_id': order_id})




@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/my_orders.html', {'orders': orders})


def product_list(request):
    products = Product.objects.all()
    return render(request, 'orders/product_list.html', {'products': products})

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    # Если кто-то попытается отменить чужой заказ, Django просто вернёт 404 (страница не найдена)
    # Можно добавить проверку, что статус позволяет отмену
    allowed_statuses = ['new', 'pending']
    if order.status not in allowed_statuses:
        messages.warning(request, 'Этот заказ нельзя отменить в текущем статусе.')
        return redirect('orders:my_orders')
    
    order.status = 'cancelled'
    order.save()
    
    messages.success(request, f'Заказ #{order.id} отменён.')
    return redirect('orders:my_orders')


@login_required
def payment_choice(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order_items = order.items.all()

    if request.method == 'POST':
        method = request.POST.get('payment_method')  # 'cash' или 'card'

        # Получаем или создаём объект Payment
        payment, created = Payment.objects.get_or_create(
            order=order,
            defaults={
                'amount': order.total_price,
                'payment_method': method,
                'is_completed': False,
            }
        )

        # Если объект уже существовал, обновляем поля (на случай изменения суммы или метода)
        if not created:
            payment.amount = order.total_price
            payment.payment_method = method
            payment.save(update_fields=['amount', 'payment_method'])

        if method == 'cash':
            # Для «При получении» просто показываем сообщение, статус не меняем
            messages.info(
                request,
                f"Данные заказа #{order.id} зафиксированы. Оплата будет произведена при получении."
            )
            return redirect('orders:my_orders')

        elif method == 'card':
            # Для онлайн‑оплаты перенаправляем на платёжную форму
            return redirect('orders:payment_card', order_id=order.id)

    return render(request, 'orders/payment_choice.html', {
        'order': order,
        'order_items': order_items,
    })
    
@login_required
def payment_card(request, order_id): 
    
    
    # Получаем заказ по ID из URL и проверяем, что он принадлежит пользователю
    order = get_object_or_404(Order, id=order_id, user=request.user)
    allowed_statuses = ['new', 'pending']
    # Проверка статуса (опционально, но полезно)
    if order.status not in allowed_statuses:
        messages.warning(request, "Этот заказ нельзя оплатить картой в текущем статусе.")
        return redirect('orders:my_orders')    
    
    return render(request, 'orders/payment_card.html', {'order': order})


# @login_required
# def payment_card(request):
#     messages.warning(request, "Это тестовая страница оплаты картой. В реальном проекте здесь будет форма.")
#     return redirect('orders:my_orders') # Для быстрого теста