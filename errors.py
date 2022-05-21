from django.http import HttpResponse
from django.shortcuts import render


def view404(request,exception):
    return render(request, "companion/404.html")

def view403(request,exception):
    return render(request, "companion/403.html")

def view500(request):
    return render(request, "companion/500.html")
