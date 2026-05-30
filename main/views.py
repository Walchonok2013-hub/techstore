from django.shortcuts import render

def index(request):
    return render(request, 'main/index.html')
def about(request):
    return render(request, 'main/about.html')

def categories(request):
    # Your logic here (e.g., get categories from database)
    return render(request, 'main/categories.html')