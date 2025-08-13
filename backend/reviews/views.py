from rest_framework import permissions, status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.conf import settings
from .models import Review
from products.models import Product
from .serializers import ReviewReadSerializer, ReviewCreateSerializer

# Toggle: public submissions allowed?
ALLOW_PUBLIC_REVIEW_SUBMISSIONS = True  # set False to restrict to admin only


class ProductReviewsView(generics.ListAPIView):
    """
    Public: list only APPROVED reviews for a product.
    GET /api/products/<product_id>/reviews/
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = ReviewReadSerializer

    def get_queryset(self):
        product_id = self.kwargs['product_id']
        return (Review.objects
                .select_related('product', 'user')
                .filter(product_id=product_id, status=Review.Status.APPROVED)
                .order_by('-created_at'))


class MyReviewsView(generics.ListAPIView):
    """
    Authenticated: list my own reviews (any status).
    GET /api/reviews/mine/
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ReviewReadSerializer

    def get_queryset(self):
        return (Review.objects
                .select_related('product', 'user')
                .filter(user=self.request.user)
                .order_by('-created_at'))


class ReviewCreateView(APIView):
    """
    Create a review (pending by default).
    POST /api/reviews/
    """
    permission_classes = [permissions.IsAuthenticated] if ALLOW_PUBLIC_REVIEW_SUBMISSIONS else [permissions.IsAdminUser]

    def post(self, request):
        ser = ReviewCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        product = get_object_or_404(Product, id=ser.validated_data['product_id'])

        # enforce one-per-user-per-product (optional, mirrors unique_together)
        if Review.objects.filter(user=request.user, product=product).exists():
            return Response({"error": "You already reviewed this product."}, status=status.HTTP_400_BAD_REQUEST)

        review = Review.objects.create(
            user=request.user if ALLOW_PUBLIC_REVIEW_SUBMISSIONS else request.user,  # same, but keeps intent clear
            product=product,
            rating=ser.validated_data['rating'],
            title=ser.validated_data.get('title', ''),
            body=ser.validated_data['body'],
            status=Review.Status.PENDING if not request.user.is_staff else Review.Status.APPROVED,
        )
        return Response({"message": "Review submitted", "review_id": review.id, "status": review.status}, status=status.HTTP_201_CREATED)

