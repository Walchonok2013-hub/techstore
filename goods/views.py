from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db import transaction
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import FormView

from cart.models import Cart
from orders.forms import CreateOrderForm
from orders.models import Order, OrderItem
from products.models import Product


class CreateOrderView(LoginRequiredMixin, FormView):
    template_name = 'orders/create_order.html'
    form_class = CreateOrderForm
    success_url = reverse_lazy('users:profile')

    def get_initial(self):
        initial = super().get_initial()
        user = self.request.user
        initial['first_name'] = user.first_name
        initial['last_name'] = user.last_name
        return initial

    def form_valid(self, form):
        try:
            with transaction.atomic():
                user = self.request.user
                cart_items = Cart.objects.filter(user=user).select_related('product')

                if not cart_items.exists():
                    messages.warning(self.request, 'Ваша корзина пуста. Добавьте товары перед оформлением заказа.')
                    return redirect('orders:create_order')

                # Создаём заказ
                order = Order.objects.create(
                    user=user,
                    phone_number=form.cleaned_data['phone_number'],
                    requires_delivery=form.cleaned_data['requires_delivery'],
                    delivery_address=form.cleaned_data['delivery_address'],
                    payment_on_get=form.cleaned_data['payment_on_get'],
                )

                # Создаём заказанные товары
                for cart_item in cart_items:
                    product = cart_item.product
                    if not product:
                        raise ValidationError(f'Товар {cart_item.id} не найден в базе данных.')

                    name = product.name
                    price = product.sell_price()
                    quantity = cart_item.quantity

                    # Проверяем количество товара на складе
                    if product.quantity < quantity:
                        raise ValidationError(
                            f'Недостаточное количество товара "{name}" на складе. '
                            f'В наличии: {product.quantity}, требуется: {quantity}.'
                        )

                    # Создаём позицию заказа
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        name=name,
                        price=price,
                        quantity=quantity,
                    )

                    # Обновляем количество товара на складе (с блокировкой строки)
                    Product.objects.filter(
                        id=product.id,
                        quantity__gte=quantity
                    ).update(quantity=product.quantity - quantity)

                # Очищаем корзину пользователя после создания заказа
                cart_items.delete()

                messages.success(self.request, 'Заказ успешно оформлен!')
                return redirect('users:profile')

        except ValidationError as e:
            messages.error(self.request, str(e))
            return redirect('orders:create_order')

        except Exception as e:
            # Логгируем ошибку для отладки
            print(f"Order creation error: {e}")  # В продакшене используйте logging
            messages.error(
                self.request,
                'Произошла ошибка при оформлении заказа. Попробуйте ещё раз или обратитесь в поддержку.'
            )
            return redirect('orders:create_order')

    def form_invalid(self, form):
        messages.error(self.request, 'Проверьте правильность заполнения формы.')
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Оформление заказа'
        context['order'] = True

        # Добавляем информацию о корзине в контекст
        user_cart = Cart.objects.filter(user=self.request.user)
        context['cart_items'] = user_cart
        context['total_price'] = sum(item.total_price() for item in user_cart)
        return context