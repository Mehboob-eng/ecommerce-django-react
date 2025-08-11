"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from myapp.views import RegisterUserAPIView, LoginAPIView, LogoutAPIView, CategoryListAPIView, ProductListAPIView,ManageProductAPIView, orderAPIView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', RegisterUserAPIView.as_view(), name='user-register'),
    path('login/', LoginAPIView.as_view(), name='user-login'),
    path('logout/', LogoutAPIView.as_view(), name='user-logout'),
    path("categories/", CategoryListAPIView.as_view(), name="category-list"),
    path("products/", ProductListAPIView.as_view(), name="product-list"),  # Assuming you want to use the same view for products
    path("manage/product/", ManageProductAPIView.as_view(), name="manage-product-list"),  # For managing products
    path("order/", orderAPIView.as_view(), name="order-list"),  # Assuming you want to use the same view for orders
]
