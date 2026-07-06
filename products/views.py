
# from django.shortcuts import render, redirect, get_object_or_404
# from django.views.decorators.http import require_POST
# from django.contrib.auth.decorators import login_required
# from products.forms import CartAddProductForm
# from products.models import Product, Category, Favorite, Cart # добавлен Favorite
# from cart.models import CartItem
# from cart.cart import Cart
# from cart.models import Cart 
# from django.core.paginator import Paginator
# from django.contrib import messages
# from django.db.models import Count, Q
# from django.db.models import Exists, OuterRef
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from django.utils.decorators import method_decorator

# from django.contrib.auth.decorators import login_required
# from django.views.decorators.http import require_http_methods
# from accounts.models import Favorite  # <-- проверь имя модели (если не Favorite — подставь своё)

from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from cart.models import CartItem
from accounts.models import Favorite
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from .models import Product, Category
from cart.cart import Cart  # Только логика корзины (сессия), без моделей
from products.forms import CartAddProductForm
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from .models import Product

from .models import Product, Category, Promotion
from accounts.models import Favorite
from .services import get_active_promotion_for_category
def search_view(request):
    query = request.GET.get('q', '')
    products = Product.objects.none()
    
    if query:
        products = Product.objects.filter(name__icontains=query)
        
    return render(request, 'products/search.html', {
        'products': products,
        'query': query
    })
    
    
    
@login_required
@require_http_methods(["POST"])
def toggle_favorite(request):
    product_id = request.POST.get('product_id')
    if not product_id:
        return JsonResponse({'success': False, 'error': 'Не указан product_id'}, status=400)

    try:
        product = Product.objects.get(pk=product_id)
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Товар не найден'}, status=404)

    favorite, created = Favorite.objects.get_or_create(user=request.user, product=product)

    if not created:
        # Если запись уже была — удаляем (переключаем «избранное»)
        favorite.delete()
        return JsonResponse({'success': True, 'action': 'removed'})

    return JsonResponse({'success': True, 'action': 'added'})

def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    if self.request.user.is_authenticated:
        # Получаем ID всех товаров, которые уже в избранном у пользователя
        fav_ids = Favorite.objects.filter(user=self.request.user).values_list('product_id', flat=True)
        context['user_favorite_ids'] = list(fav_ids)
    return context

@require_POST
@csrf_exempt
@login_required  # если нужно только для авторизованных
def add_to_cart(request):
    product_id = request.POST.get('product_id')
    quantity = int(request.POST.get('quantity', 1))

    try:
        product = Product.objects.get(id=product_id, is_active=True)
        if not product.available:
            return JsonResponse({
                'success': False,
                'message': f'Товар "{product.name}" временно недоступен'
            })

        # Логика добавления в корзину (для авторизованных и гостей)
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': quantity}
            )
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            cart_count = cart.items.count()
        else:
            # Для гостей — используйте сессионную корзину
            from cart.cart import Cart as SessionCart
            session_cart = SessionCart(request)
            session_cart.add(product=product, quantity=quantity)
            cart_count = len(session_cart)

        return JsonResponse({
            'success': True,
            'message': f'{product.name} добавлен в корзину!',
            'cart_count': cart_count
        })
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Товар не найден'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


def home_page(request):
    popular_products = Product.objects.filter(
        is_active=True,
        available=True,
        is_popular=True
    )[:8]
    context = {'popular_products': popular_products}
    return render(request, 'products/home.html', context)

def product_list(request):
    queryset = Product.objects.all()

    # Фильтр по категории
    category_id = request.GET.get("category")
    if category_id:
        queryset = queryset.filter(category_id=category_id)

    # Фильтр по цене (мин/макс)
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")

    if min_price:
        queryset = queryset.filter(price__gte=min_price)
    if max_price:
        queryset = queryset.filter(price__lte=max_price)

    categories = Category.objects.all()

    context = {
        "products": queryset,
        "categories": categories,
    }
    return render(request, "products/catalog.html", context)

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True, available=True)
    cart = Cart(request)
    form = CartAddProductForm()
    
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(user=request.user, product=product).exists()

    return render(request, 'products/product_detail.html', {
        'product': product,
        'category': product.category,  # <-- Добавь эту строку
        'form': form,
        'cart': cart,
        'is_favorite': is_favorite
    })


def product_detail_view(request, slug):
    # Ищем товар по полю slug. Если нет - вернем 404
    product = get_object_or_404(Product, slug=slug)
    
    context = {
        'product': product,
        # Добавьте сюда другие нужные переменные, если есть
    }
    return render(request, 'products/product_detail.html', context)

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug, is_active=True)
    products = category.products.filter(is_active=True, available=True)
    # ... тут можно добавить пагинацию как в catalog_view ...
    return render(request, 'products/category_detail.html', {'category': category, 'products': products})


def catalog(request):
    products = Product.objects.all()
    categories = Category.objects.all()

    # Логика фильтрации (по категории, цене и т. д.)
    category_id = request.GET.get('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if category_id:
        products = products.filter(category_id=category_id)
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    # Добавляем флаг is_favorite для каждого товара
    if request.user.is_authenticated:
        favorite_ids = Favorite.objects.filter(user=request.user).values_list('product_id', flat=True)
        for product in products:
            product.is_favorite = product.id in favorite_ids

    context = {
        'products': products,
        'categories': categories,
    }
    return render(request, 'products/catalog.html', context)

def search(request):
    query = request.GET.get('q', '')
    products = Product.objects.none()

    if query:
        products = Product.objects.filter(name__icontains=query)

    return render(request, 'products/search.html', {
        'products': products,
        'query': query
    })
@require_POST    
@csrf_protect
def add_to_cart(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Метод не разрешён'}, status=405)

    product_id = request.POST.get('product_id')
    try:
        quantity = int(request.POST.get('quantity', 1))
        if quantity < 1:
            quantity = 1
    except (ValueError, TypeError):
        return JsonResponse({'success': False, 'message': 'Некорректное количество'}, status=400)

    try:
        product = Product.objects.get(id=product_id, is_active=True, available=True)
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Товар не найден'}, status=404)

    cart = Cart(request)

    # 1. Получаем лучшую акцию для категории товара
    promotion = get_active_promotion_for_category(product.category)

    # 2. Считаем цены
    original_price = product.price  # Decimal из модели
    final_price = original_price

    if promotion:
        discount = promotion.get_discount_amount(original_price)
        final_price = original_price - discount

    # 3. Добавляем в корзину с обеими ценами
    cart.add(
        product=product,
        quantity=quantity,
        price=final_price,          # цена со скидкой (платит клиент)
        original_price=original_price,  # полная цена (для расчёта скидки в заказе)
        update_quantity=False
    )

    # 4. Формируем ответ
    referer = request.META.get('HTTP_REFERER')
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    response_data = {
        'success': True,
        'message': f'{product.name} добавлен в корзину!',
        'cart_count': len(cart),
        'item_total_price': str(final_price * quantity),
    }

    if is_ajax:
        return JsonResponse(response_data)

    if referer:
        return redirect(referer)

    return redirect('products:catalog')    
#@require_POST
# @csrf_protect
# def add_to_cart(request):
#     product_id = request.POST.get('product_id')
#     quantity = int(request.POST.get('quantity', 1))
#     if quantity < 1:
#         quantity = 1

#     try:
#         product = Product.objects.get(id=product_id, is_active=True, available=True)
#     except Product.DoesNotExist:
#         return JsonResponse({'success': False, 'message': 'Товар не найден'}, status=404)

#     cart = Cart(request)
#     cart.add(product=product, quantity=quantity, update_quantity=False)

#     referer = request.META.get('HTTP_REFERER')
#     if referer:
#         # Если это AJAX-запрос — верни JSON, иначе редирект
#         if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
#             return JsonResponse({
#                 'success': True,
#                 'message': f'{product.name} добавлен в корзину!',
#                 'cart_count': len(cart)
#             })
#         return redirect(referer)

#     return redirect('products:catalog')


@login_required
def cart_view(request):
    """Альтернативное представление для авторизованных пользователей (если нужно)"""
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.get_total_price() for item in cart_items)
    return render(request, 'cart/cart.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })

def cart_detail(request):
    """Отображение содержимого корзины"""
    cart = Cart(request)
    cart_items = cart.get_items()  # или ваша логика получения элементов
    total_price = cart.get_total_price()

    return render(request, 'products/cart_detail.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })

def delivery(request):
    return render(request, 'products/delivery.html')

def contacts(request):
    return render(request, 'products/contacts.html')


def about(request):
    return render(request, 'products/about.html')

def catalog_view(request):
    products = Product.objects.filter(is_active=True, available=True)

    # Фильтры
    category_id = request.GET.get('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if category_id:
        products = products.filter(category_id=category_id)
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    # Пагинация
    paginator = Paginator(products, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Проверка избранного
    fav_ids = set()
    if request.user.is_authenticated:
        fav_ids = set(Favorite.objects.filter(user=request.user).values_list('product_id', flat=True))

    # Подготовка данных для отображения скидок
    # Сначала соберём все категории, которые встречаются на странице, чтобы не делать N+1 запросов
    categories_on_page = {p.category for p in page_obj if p.category}
    promotions_by_category = {}
    for cat in categories_on_page:
        promo = get_active_promotion_for_category(cat)
        if promo:
            promotions_by_category[cat.id] = promo

    # Добавляем атрибуты к каждому товару
    for product in page_obj:
        product.is_favorite = product.id in fav_ids

        # Скидка
        promo = promotions_by_category.get(product.category_id) if product.category else None
        if promo:
            product.promotion = promo
            discount_factor = 1 - (promo.discount_percent / 100)
            product.final_price = round(float(product.price) * discount_factor, 2)
            product.discount_amount = round(float(product.price) - product.final_price, 2)
        else:
            product.promotion = None
            product.final_price = float(product.price)
            product.discount_amount = 0.0

    context = {
        'products': page_obj,
        'categories': Category.objects.filter(is_active=True),
        'filters': request.GET,
    }
    return render(request, 'products/catalog.html', context)
# def catalog_view(request):
#     products = Product.objects.filter(is_active=True, available=True)
    
#     # Фильтры
#     category_id = request.GET.get('category')
#     min_price = request.GET.get('min_price')
#     max_price = request.GET.get('max_price')

#     if category_id:
#         products = products.filter(category_id=category_id)
#     if min_price:
#         products = products.filter(price__gte=min_price)
#     if max_price:
#         products = products.filter(price__lte=max_price)

#     # Пагинация
#     paginator = Paginator(products, 9)
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)

#     # Проверка избранного для отображения сердечек сразу при загрузке
#     fav_ids = set()
#     if request.user.is_authenticated:
#         fav_ids = set(Favorite.objects.filter(user=request.user).values_list('product_id', flat=True))
    
#     for product in page_obj:
#         product.is_favorite = product.id in fav_ids

#     context = {
#         'products': page_obj,
#         'categories': Category.objects.filter(is_active=True),
#         'filters': request.GET
#     }
#     return render(request, 'products/catalog.html', context)
