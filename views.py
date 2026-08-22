from django.shortcuts import render

def home(request):
    return render(request, 'home.html')  # или верните нужный контент