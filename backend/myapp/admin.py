from django.contrib import admin

from .models import Users, Category, Product
admin.site.register(Users)
admin.site.register(Category)
admin.site.register(Product)

# Register your models here.
