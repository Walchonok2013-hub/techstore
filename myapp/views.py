from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    return HttpResponse("Добро пожаловать !")

def info(request):
    return render(request, 'info/index.html')

def delivery(request):
    return render(request, 'info/delivery.html')

def contacts(request):
    return render(request, 'info/contacts.html')

def about(request):
    return render(request, 'info/about.html')
