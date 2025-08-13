from django.shortcuts import render

from django.http import JsonResponse

def get_categories(request):
    return JsonResponse({"message": "Categories list"})

