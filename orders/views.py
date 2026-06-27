
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import OrderCreateForm
from cart.cart import Cart
from .models import Order, OrderItem, Product
from .models import Order
from django.db import transaction
from django.contrib import messages
from django.shortcuts import render, redirect
import logging
from .models import Order
from .forms import OrderCreateForm 
from cart.cart import Cart  

logger = logging.getLogger(__name__)


@login_required
def order_create(request):
    cart = Cart(request)
    
    if len(cart) == 0:  # проверяем количество товаров в корзине
        messages.error(request, "Ваша корзина пуста.")
        return redirect('cart:cart_detail')

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Создаём заказ
                    order = form.save(commit=False)
                    order.user = request.user
                    order.status = 'NEW'
                    order.save()

                    # Добавляем товары из корзины в заказ
                    items_created = 0
                    for item in cart:
                        OrderItem.objects.create(
                            order=order,
                            product=item['product'],
                            price=item['price'],
                            quantity=item['quantity']
                        )
                        items_created += 1

                    # Очищаем корзину
                    cart.clear()

                    logger.info(f"Заказ #{order.id} успешно создан пользователем {request.user.username}. Добавлено товаров: {items_created}")
                    messages.success(request, f"Заказ #{order.id} успешно оформлен!")
                    logger.info(f"Попытка перенаправления на страницу подтверждения для заказа #{order.id}")
                    
                    return redirect('orders:order_confirmation', order.id)

            except Exception as e:
                logger.error(f"Ошибка при создании заказа для пользователя {request.user.username}: {str(e)}")
                messages.error(request, "Произошла ошибка при оформлении заказа. Пожалуйста, попробуйте ещё раз.")
                # Если произошла ошибка, транзакция откатится автоматически благодаря transaction.atomic()
                return render(request, 'orders/create.html', {'form': form})
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки в форме.")
            logger.warning(f"Ошибки валидации формы заказа для пользователя {request.user.username}: {form.errors}")
    else:
        form = OrderCreateForm()

    return render(request, 'orders/create.html', {
        'form': form,
        'cart': cart
    })
    
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'admin/orders/order/detail.html', {'order': order})



def order_created(request, order_id):
    return render(request, 'orders/created.html', {'order_id': order_id})

def order_confirmation(request, order_id):
    # Получаем заказ или выдаём ошибку 404, если не найден
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'orders/confirmation.html', {'order': order})


@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created')
    return render(request, 'orders/my_orders.html', {'orders': orders})


def product_list(request):
    products = Product.objects.all()
    return render(request, 'orders/product_list.html', {'products': products})




@login_required
def create_order_view(request):
    cart = Cart(request)
    if not cart:  # или len(cart) == 0, зависит от реализации
        return redirect('products:catalog')


    if request.method == 'POST':
        form = OrderCreateForm(request.POST)  # <-- Используем OrderCreateForm
        if form.is_valid():
            # Считаем полную стоимость ДО скидки
            base_price = sum(item['quantity'] * item['product'].price for item in cart)
            
            # Твоя логика скидки (сейчас 0)
            discount_amount = base_price * 0.2 
            
            final_price = base_price - discount_amount
            if final_price < 0:
                final_price = 0

            order = Order.objects.create(
                user=request.user,
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone'],
                address=form.cleaned_data['address'],
                notes=form.cleaned_data.get('notes', ''),
                
                original_total=base_price,
                discount=discount_amount,
                total_price=final_price,
                status='new',
            )

            cart.clear()
            return redirect('orders:order_created', order_id=order.id)
    else:
        form = OrderCreateForm()  # <-- Создаём пустую форму

    return render(request, 'orders/checkout.html', {'form': form, 'cart': cart})


# @login_required
# def create_order_view(request):
#     cart = Cart(request)
    
#     if request.method == 'POST':
#         form = OrderCreateForm(request.POST)  # предположим, что у тебя есть форма OrderForm
#         if form.is_valid():
#             # 1. Считаем полную стоимость ДО скидки (base_price)
#             base_price = sum(item['quantity'] * item['product'].price for item in cart)
            
#             # 2. Считаем скидку (если у тебя есть логика скидок — например, промокод или процент)
#             # Если скидок нет, просто ставь 0
#             discount_amount = base_price * 0.2  # <-- Вставь сюда свою логику расчёта скидки
            
#             # 3. Считаем итоговую цену
#             final_price = base_price - discount_amount
#             if final_price < 0:
#                 final_price = 0

#             # 4. Создаём заказ, обязательно заполняя original_total
#             order = Order.objects.create(
#                 user=request.user,
#                 first_name=form.cleaned_data['first_name'],
#                 last_name=form.cleaned_data['last_name'],
#                 email=form.cleaned_data['email'],
#                 phone=form.cleaned_data['phone'],
#                 address=form.cleaned_data['address'],
#                 notes=form.cleaned_data.get('notes', ''),
                
#                 original_total=base_price,      # <-- Полная стоимость ДО скидки
#                 discount=discount_amount,        # <-- Сумма скидки в рублях
#                 total_price=final_price,         # <-- Итоговая цена к оплате
#                 status='new',
#             )

#             # 5. Сохраняем позиции заказа (если у тебя есть модель OrderItem)
#             # Если её нет — этот блок можно пропустить
#             for item in cart:
#                 product = item['product']
#                 quantity = item['quantity']
#                 price = product.price
#                 # Здесь можно создать OrderItem(order=order, product=product, quantity=quantity, price=price)

#             # 6. Очищаем корзину
#             cart.clear()

#             return redirect('orders:order_created', order_id=order.id)
#     else:
#         form = OrderForm()

#     return render(request, 'orders/checkout.html', {'form': form, 'cart': cart})

def payment_view(request):
    if request.method == 'POST':
        # сохраняем данные заказа в БД
        return redirect('orders:payment_form')  # перенаправление на форму оплаты
    else:
        return render(request, 'orders/payment.html')

def payment_form_view(request):
    # отображаем страницу с формой оплаты
    return render(request, 'orders/payment_form.html')  # не redirect, а render!

