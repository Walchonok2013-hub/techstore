from django.shortcuts import render

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