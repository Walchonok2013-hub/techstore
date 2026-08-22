from django.shortcuts import render
from .models import DeliveryMethod, PaymentMethod


    
def index(request):
    return render(request, 'main/index.html')
def about(request):
    return render(request, 'main/about.html')
def delivery(request):
    return render(request, 'main/delivery.html')
def contacts(request):
    return render(request, 'main/contacts.html')
def categories(request):

    return render(request, 'main/categories.html')
def delivery_payment(request):
    delivery_methods = [
        {'name': 'Курьерская доставка', 'price': '300 руб.', 'description': '1–2 рабочих дня, с 9:00 до 21:00'},
        {'name': 'Самовывоз', 'price': 'Бесплатно', 'description': 'г. Москва, ул. Примерная, д. 1, 9:00–21:00'}
    ]
    payment_methods = [
        {'name': 'Банковской картой онлайн', 'description': 'Visa, Mastercard, Мир'},
        {'name': 'Наличными при получении', 'description': 'Только при курьерской доставке'}
    ]
    return render(request, 'delivery_payment.html', {
        'delivery_methods': delivery_methods,
        'payment_methods': payment_methods
    })
def delivery(request):
    delivery_methods = DeliveryMethod.objects.filter(is_active=True)
    payment_methods = PaymentMethod.objects.filter(is_active=True)

    context = {
        'delivery_methods': delivery_methods,
        'payment_methods': payment_methods
    }
    return render(request, 'main/delivery.html', context)
