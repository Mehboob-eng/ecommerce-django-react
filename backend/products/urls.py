from django.urls import path
from . import views
from .views import ProductListCreate


urlpatterns = [
     path("", ProductListCreate.as_view(), name="products"),
    path('', views.ProductList.as_view(), name='product-list'),

]
