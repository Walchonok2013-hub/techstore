from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from products.forms import CartAddProductForm
from products.models import Product, Category
from cart.models import CartItem
from cart.cart import Cart
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Count, Q
def home_page(request):
    categories = Category.objects.annotate(
        product_count=Count('products', filter=Q(products__is_active=True))
    ).order_by('name')
    popular_products = Product.objects.filter(is_active=True)[:8]
    latest_products = Product.objects.filter(is_active=True).order_by('-created_at')[:8]

    return render(request, 'products/home.html', {
        'categories': categories,
        'popular_products': popular_products,
        'latest_products': latest_products
    })


def product_list(request):
    products = Product.objects.filter(is_active=True)
    paginator = Paginator(products, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Используем сессионную корзину для всех пользователей
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

def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug)
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


def home(request):
    popular_products = Product.objects.filter(is_popular=True, available=True)
    all_products = Product.objects.all()[:8]

    return render(request, 'products/home.html', {
    'popular_products': popular_products,
    'all_products': all_products
})