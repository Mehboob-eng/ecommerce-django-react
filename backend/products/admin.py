from django.contrib import admin

from .models import Category, Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['name','description']
    

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']