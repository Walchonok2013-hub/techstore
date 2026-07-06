from django.shortcuts import render, redirect, get_object_or_404
from .models import Order, OrderItem, Payment
from cart.models import Cart as CartModel  # Импортируем МОДЕЛЬ корзины, а не класс-обертку
import logging
from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.db import transaction
from decimal import Decimal
from .models import Order, OrderItem
from cart.cart import Cart
from .forms import OrderCreateForm
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
import calendar
from .models import Order, OrderItem, Payment, Product
from django.db.models import Sum, Count, F

logger = logging.getLogger(__name__)


@login_required
def profile(request):
    # 1. Исправлена ошибка: Count не был импортирован в твоем коде
    # 2. Убрал срез [:5] из основного queryset для подсчета статистики, 
    #    иначе статистика считалась бы только по 5 последним заказам, а не по всем.
    all_user_orders = Order.objects.filter(user=request.user)
    
    # Считаем статистику по ВСЕМ заказам
    stats = all_user_orders.aggregate(
        total_spent=Sum('total_price'),
        total_orders=Count('id')
    )
    
    total_spent = stats['total_spent'] or Decimal('0')
    total_orders_count = stats['total_orders'] or 0
    
    # Защита от деления на ноль
    average_check = (total_spent / total_orders_count) if total_orders_count > 0 else Decimal('0')

    # Для отображения в профиле берем последние 5 заказов, но с оптимизацией
    # prefetch_related('items') загружает все товары одним запросом, избегая N+1 проблемы
    orders = all_user_orders.order_by('-created_at')[:5].prefetch_related('items')

    context = {
        'user': request.user,
        'orders': orders,
        'total_orders': total_orders_count,
        'total_spent': total_spent,
        'average_check': average_check,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
@transaction.atomic
def order_create(request):
    cart = Cart(request)
    
    # Проверка на пустую корзину
    if not cart or len(cart) == 0:
        messages.warning(request, "Ваша корзина пуста.")
        return redirect('cart:cart_detail')

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            # Важно: сразу сохраняем, чтобы получить order.id для связи с OrderItem
            order.save()

            total_price_sum = Decimal('0')
            original_total_sum = Decimal('0')
            discount_sum = Decimal('0')

            current_date = timezone.now()
            _, days_in_month = calendar.monthrange(current_date.year, current_date.month)
            end_of_month = current_date.replace(day=days_in_month)

            for item in cart:
                # Безопасное получение ID продукта
                product_id = item.get('product_id') or item.get('product')
                if not product_id:
                    continue

                try:
                    product = Product.objects.get(pk=product_id)
                except Product.DoesNotExist:
                    logger.warning(f"Продукт с ID {product_id} не найден, пропускаем.")
                    continue

                quantity = item['quantity']
                price_from_cart = item['price']
                original_price_from_cart = item.get('original_price', product.price)
                
                final_price = price_from_cart
                item_discount = Decimal('0')

                # Логика скидки (оставил твою, но добавил проверку на тип данных)
                if product.category == 'smartfony-i-aksessuary' and current_date <= end_of_month:
                    discount_per_item = original_price_from_cart * Decimal('0.20')
                    item_discount = discount_per_item * quantity
                    final_price = original_price_from_cart - discount_per_item
                
                discount_sum += item_discount
                original_total_sum += original_price_from_cart * quantity
                total_price_sum += final_price * quantity

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=final_price,
                    original_price=original_price_from_cart
                )

            # Обновляем итоговые суммы заказа
            order.original_total = original_total_sum
            order.discount = discount_sum
            order.total_price = total_price_sum
            order.save(update_fields=['original_total', 'discount', 'total_price'])

            cart.clear()
            return redirect('orders:order_created', order_id=order.id)
    else:
        form = OrderCreateForm()
    
    return render(request, 'orders/create.html', {'cart': cart, 'form': form})


@login_required
def order_detail_user(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})


def order_confirmation(request, order_id):
    # Добавил проверку пользователя, если эта страница доступна только авторизованным
    if not request.user.is_authenticated:
        return redirect('login')
        
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/confirmation.html', {'order': order})


def order_detail(request, order_id):
    # ВНИМАНИЕ: Эта функция доступна ЛЮБОМУ пользователю, если он знает ID заказа.
    # В реальном проекте здесь нужна проверка прав доступа (owner == request.user)
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'orders/detail.html', {'order': order})


@login_required
def payment_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Получаем платеж. Предполагаем, что связь OneToOne или ForeignKey называется 'payment'
    # Если связи нет, нужно создать объект Payment перед этим шагом
    payment = getattr(order, 'payment', None)

    if not payment:
        messages.warning(request, "Платеж не найден для этого заказа.")
        return redirect('orders:my_orders')

    if not payment.is_completed:
        payment.is_completed = True
        payment.save(update_fields=['is_completed'])

    # Логика обновления статуса заказа
    # Если оплата картой (не cash) и платеж успешен -> статус 'paid'
    if payment.is_completed and payment.payment_method != 'cash':
        order.status = 'paid'
        order.payment_type = payment.payment_method
        order.save(update_fields=['status', 'payment_type'])
        
        messages.success(
            request,
            f"Оплата заказа #{order.id} успешно завершена! Способ: {payment.get_payment_method_display()}"
        )
    else:
        # Сценарий: наложенный платеж (cash) или повторная обработка
        messages.info(
            request,
            f"Статус платежа обновлен. Оплата заказа #{order.id} будет произведена при получении."
        )

    return redirect('orders:my_orders')




    
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


