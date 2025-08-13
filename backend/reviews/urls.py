from django.urls import path
from .views import ProductReviewsView, ReviewCreateView, MyReviewsView

urlpatterns = [
    path('products/<int:product_id>/reviews/', ProductReviewsView.as_view(), name='product-reviews'),
    path('reviews/', ReviewCreateView.as_view(), name='review-create'),
    path('reviews/mine/', MyReviewsView.as_view(), name='my-reviews'),
]
