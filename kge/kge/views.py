from django.shortcuts import render

def home(request):
    return render(request, 'base.html')

def info_kolbaszflix(request):
    return render(request, 'info_kolbaszflix.html')