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
from myapp.views import RegisterUserAPIView,ReviewListAPIView,ReviewAPIView,hello_world,ManageCategoryAPIView ,LoginAPIView, LogoutAPIView,manageOrderAPIView, CategoryListAPIView, ProductListAPIView,ManageProductAPIView, orderAPIView
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', RegisterUserAPIView.as_view(), name='user-register'),
    path('login/', LoginAPIView.as_view(), name='user-login'),
    path('logout/', LogoutAPIView.as_view(), name='user-logout'),
    path("categories/", CategoryListAPIView.as_view(), name="category-list"),
    path("products/", ProductListAPIView.as_view(), name="product-list"),  # Assuming you want to use the same view for products
    
    path("manage/product/", ManageProductAPIView.as_view(), name="manage-product-list"),  # For managing products
    path("order/", orderAPIView.as_view(), name="order-list"),  # Assuming you want to use the same view for orders
    path("manage/category/", ManageCategoryAPIView.as_view(), name="manage-category-list"),  # For managing categories
    path("manage/review/", ReviewAPIView.as_view(), name="review-list"),  # Assuming you want to use the same view for reviews
    path("product/<int:pk>/reviews/", ReviewListAPIView.as_view(), name="product-review-list"),  # For listing reviews of a specific product
    path("manage/order/", manageOrderAPIView.as_view(), name="manage-order-list"),  # For managing orders
    path("api/hello/", hello_world.as_view(), name="hello-world"),  # Example API endpoint
    ]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
