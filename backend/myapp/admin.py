from django.contrib import admin

from .models import Users, Category, Product, Order,review
admin.site.register(Users)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(review)
# Register your models here.
