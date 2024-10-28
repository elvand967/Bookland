# D:\Python\myProject\Bookland\apps\bookland\views.py

from django.http import HttpResponse
from django.shortcuts import render


def index(request):
    return HttpResponse('<a href="http://127.0.0.1:8000/admin/"> Админ-панель </a>')
