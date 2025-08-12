from django.contrib import admin

from .models import Users, Category, Product, Order
admin.site.register(Users)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Order)
# Register your models here.
