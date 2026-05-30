from django.shortcuts import render

# Create your views here.


from .models import Product

def product_list(request):
    products = Product.objects.all()
    return render(request, 'shop/product_list.html', {'products': products})