
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from products.forms import CartAddProductForm
from products.models import Product, Category, Favorite, Cart # добавлен Favorite
from cart.models import CartItem
from cart.cart import Cart
from cart.models import Cart 
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Count, Q
from django.db.models import Exists, OuterRef
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator


from .models import Favorite
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

@login_required
@csrf_exempt
def toggle_favorite(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')

        try:
            product = Product.objects.get(id=product_id)
            favorite, created = Favorite.objects.get_or_create(
                user=request.user,
                product=product
            )

            if not created:
                # Если уже в избранном — удаляем
                favorite.delete()
                return JsonResponse({
                    'success': True,
                    'is_favorite': False,
                    'message': 'Товар удалён из избранного'
                })
            else:
                return JsonResponse({
                    'success': True,
                    'is_favorite': True,
                    'message': 'Товар добавлен в избранное'
                })
        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Товар не найден'})

    return JsonResponse({'success': False, 'message': 'Ошибка запроса'})

# from django.shortcuts import render, redirect, get_object_or_404
# from django.views.decorators.http import require_POST
# from django.contrib.auth.decorators import login_required
# from products.forms import CartAddProductForm
# from products.models import Product, Category
# from cart.models import CartItem
# from cart.cart import Cart
# from django.core.paginator import Paginator
# from django.contrib import messages
# from django.db.models import Count, Q
# from django.db.models import Exists, OuterRef
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from django.utils.decorators import method_decorator
# from cart.models import CartItem
# from .models import Favorite, Product
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from django.utils.decorators import method_decorator
# from django.contrib.auth.decorators import login_required


# from .models import Product
# @require_POST
# @csrf_exempt
# @login_required  # если нужно только для авторизованных
# def add_to_cart(request):
#     product_id = request.POST.get('product_id')
#     quantity = int(request.POST.get('quantity', 1))

#     try:
#         product = Product.objects.get(id=product_id, is_active=True)
#         if not product.available:
#             return JsonResponse({
#                 'success': False,
#                 'message': f'Товар "{product.name}" временно недоступен'
#             })

#         # Логика добавления в корзину (для авторизованных и гостей)
#         if request.user.is_authenticated:
#             cart, created = Cart.objects.get_or_create(user=request.user)
#             cart_item, created = CartItem.objects.get_or_create(
#                 cart=cart,
#                 product=product,
#                 defaults={'quantity': quantity}
#             )
#             if not created:
#                 cart_item.quantity += quantity
#                 cart_item.save()
#             cart_count = cart.items.count()
#         else:
#             # Для гостей — используйте сессионную корзину
#             from cart.cart import Cart as SessionCart
#             session_cart = SessionCart(request)
#             session_cart.add(product=product, quantity=quantity)
#             cart_count = len(session_cart)

#         return JsonResponse({
#             'success': True,
#             'message': f'{product.name} добавлен в корзину!',
#             'cart_count': cart_count
#         })
#     except Product.DoesNotExist:
#         return JsonResponse({'success': False, 'message': 'Товар не найден'})
#     except Exception as e:
#         return JsonResponse({'success': False, 'message': str(e)})







# @login_required
# @csrf_exempt
# def toggle_favorite(request):
#     if request.method == 'POST':
#         product_id = request.POST.get('product_id')

#         try:
#             product = Product.objects.get(id=product_id)
#             favorite, created = Favorite.objects.get_or_create(
#                 user=request.user,
#                 product=product
#             )

#             if not created:
#                 # Если уже в избранном — удаляем
#                 favorite.delete()
#                 return JsonResponse({
#                     'success': True,
#                     'is_favorite': False,
#                     'message': 'Товар удалён из избранного'
#                 })
#             else:
#                 return JsonResponse({
#                     'success': True,
#                     'is_favorite': True,
#                     'message': 'Товар добавлен в избранное'
#                 })
#         except Product.DoesNotExist:
#             return JsonResponse({'success': False, 'message': 'Товар не найден'})

#     return JsonResponse({'success': False, 'message': 'Ошибка запроса'})

# def home(request):
#     popular_products = Product.objects.filter(is_popular=True, available=True)
#     all_products = Product.objects.all()[:8]

#     return render(request, 'products/home.html', {
#     'popular_products': popular_products,
#     'all_products': all_products
# })

# def home_page(request):
#     categories = Category.objects.annotate(
#         product_count=Count('products', filter=Q(products__is_active=True))
#     ).order_by('name')
#     popular_products = Product.objects.filter(is_active=True)[:8]
#     latest_products = Product.objects.filter(is_active=True).order_by('-created_at')[:8]

#     return render(request, 'products/home.html', {
#         'categories': categories,
#         'popular_products': popular_products,
#         'latest_products': latest_products
#     })

def home_page(request):
    categories = Category.objects.annotate(
        product_count=Count('products', filter=Q(products__is_active=True))
    ).order_by('name')
    
    # ИСПРАВЛЕНИЕ: Фильтруем по is_popular и is_active
    popular_products = Product.objects.filter(is_popular=True, is_active=True)[:8]
    
    latest_products = Product.objects.filter(is_active=True).order_by('-created_at')[:8]

    return render(request, 'products/home.html', {
        'categories': categories,
        'popular_products': popular_products,
        'latest_products': latest_products
    })

def product_list(request):
    products = Product.objects.filter(is_active=True)

    # Добавляем аннотацию для избранного
    if request.user.is_authenticated:

        products = products.annotate(
            is_favorite=Exists(
                Favorite.objects.filter(
                    user=request.user,
            product=OuterRef('pk')
        )
    )
)
    paginator = Paginator(products, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Для корзины — используем сессионный подход
    cart = Cart(request)
    cart_product_ids = [str(item['product'].id) for item in cart]

    return render(request, 'products/product_list.html', {
        'page_obj': page_obj,
        'products': page_obj.object_list,
        'cart_product_ids': cart_product_ids
    })
    
# def product_detail(request, id, slug):
#     product = get_object_or_404(Product, id=id, slug=slug)
#     category = product.category  # получаем категорию товара


#     cart_product_form = CartAddProductForm()

#     return render(request, 'products/product_detail.html', {
#         'product': product,
#         'cart_product_form': cart_product_form,
#         'category': category  # передаём категорию в шаблон
#     })

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    category = product.category

    cart_product_form = CartAddProductForm()

    # Получаем словарь характеристик
    specifications_dict = product.get_specifications_dict()

    return render(request, 'products/product_detail.html', {
        'product': product,
        'cart_product_form': cart_product_form,
        'category': category,
        'specifications_dict': specifications_dict  # передаём словарь в шаблон
    })


#     cart_product_form = CartAddProductForm()

#     return render(request, 'products/product_detail.html', {
#         'product': product,
#         'cart_product_form': cart_product_form,
#         'category': category  # передаём категорию в шаблон
#     })

# def category_detail(request, slug):
#     print(f"[DEBUG] Получен slug: '{slug}'")
#     try:
#         category = Category.objects.get(slug=slug, is_active=True)
#         print(f"[DEBUG] Найдена категория: {category.name} (ID: {category.id})")
#     except Category.DoesNotExist:
#         print(f"[DEBUG] Категория с slug='{slug}' не найдена")
#         raise
#     products = Product.objects.filter(category=category, is_active=True)
#     context = {'category': category, 'products': products}
#     return render(request, 'products/category_detail.html', context)
# ЕДИНСТВЕННАЯ ВЕРСИЯ category_detail — корректная
def category_detail(request, slug):
    # Получаем категорию по slug
    category = get_object_or_404(Category, slug=slug)

    # Фильтруем активные товары в этой категории
    products = Product.objects.filter(
        category=category,
        is_active=True
    ).select_related('category')  # оптимизируем запросы к БД

    return render(request, 'products/category_detail.html', {
        'category': category,
        'products': products
    })

def catalog(request):
    products = Product.objects.all()
    return render(request, 'products/catalog.html', {'products': products})

def search(request):
    query = request.GET.get('q', '')
    products = Product.objects.none()

    if query:
        products = Product.objects.filter(name__icontains=query)

    return render(request, 'products/search.html', {
        'products': products,
        'query': query
    })
@csrf_exempt
@login_required
@require_POST
def cart_add(request, product_id):
    """Добавление товара в корзину (работает для гостей и авторизованных)"""
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)

    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        quantity = cd['quantity']

        # Проверка доступности товара
        if not product.available:
            messages.error(request, f'Товар "{product.name}" временно недоступен')
            return redirect('products:product_list')
        # Добавление в корзину
        cart.add(product=product, quantity=quantity, update_quantity=cd['update'])
        messages.success(request, f'Товар "{product.name}" добавлен в корзину')
    else:
        messages.error(request, 'Некорректные данные. Проверьте количество товара.')
    return redirect('cart:cart_detail')


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

# def catalog_view(request):
#     return render(request, 'products/catalog.html')


# def home(request):
#     products = Product.objects.all()[:8]
#     context = {'products': products}
#     return render(request, 'products/home.html', context)


