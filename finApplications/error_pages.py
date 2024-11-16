from django.shortcuts import render
import os

def custom_404_view(request, exception):
    """Кастомная страница для ошибки 404"""
    return render(request, os.path.join('../templates', '404.html'), status=404)

def custom_500_view(request):
    """Кастомная страница для ошибки 500"""
    return render(request, os.path.join('../templates', '500.html'), status=500)
