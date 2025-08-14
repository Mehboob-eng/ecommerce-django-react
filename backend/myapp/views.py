# views.py
from rest_framework import generics
from .Serilizer import UserRegisterSerializer, LoginSerializer,ReviewSerializer ,CategorySerializer, ProductSerializer,OrderSerializer
from .models import Users, Category, Product, Order, review
from .Permission import IsStaffUser
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

class hello_world(APIView):

    def get(self, request):
        return Response({"message": "Hello, world!"}, status=status.HTTP_200_OK)

class RegisterUserAPIView(APIView):
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "User created successfully", "user_id": user.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginAPIView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'username': user.username
        }, status=status.HTTP_200_OK)
    
class LogoutAPIView(APIView):
    permission_classes = [ permissions.IsAuthenticated ]
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "User logged out successfully"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class CategoryListAPIView(APIView):
    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ManageCategoryAPIView(APIView):
    """API view for managing categories (create, update, delete)"""
    permission_classes = [IsStaffUser]

    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            category = serializer.save()
            return Response({"message": "Category created successfully", "category_id": category.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def put(self, request):
        """Update a category"""
        category_id = request.data.get("id")
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = CategorySerializer(category, data=request.data, partial=True)
        if serializer.is_valid():
            category = serializer.save()
            return Response({"message": "Category updated successfully", "category_id": category.id}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def delete(self, request):
        """Delete a category"""
        category_id = request.data.get("id")
        try:
            category = Category.objects.get(id=category_id)
            category.delete()
            return Response({"message": "Category deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Category.DoesNotExist:
            return Response({"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND)
    
class ProductListAPIView(APIView):

    def get(self, request,pk=None):
        """List all products""" 
        if pk:
            products = Product.objects.filter(category_id=pk)
        else:
            products = Product.objects.all()
        serializer = ProductSerializer(products, many=True ,context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    
class ManageProductAPIView(APIView):
    permission_classes = [IsStaffUser]

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            product = serializer.save()
            return Response({"message": "Product created successfully", "product_id": product.id}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        """Update a product"""
        product_id = request.data.get("id")
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            product = serializer.save()
            return Response({"message": "Product updated successfully", "product_id": product.id}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def delete(self, request):
        product_id = request.data.get("id")
        try:
            product = Product.objects.get(id=product_id)
            product.delete()
            return Response({"message": "Product deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

class orderAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        product_id = request.data.get("product")
        quantity = request.data.get("quantity")
        address = request.data.get("address")
        # Product exist check
        product = Product.objects.filter(id=product_id).first()
        if not product:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        # Stock check
        if product.stock < quantity:
            return Response({"error": "Insufficient stock"}, status=status.HTTP_400_BAD_REQUEST)
        # Order create
        order = Order.objects.create(
            user=request.user,
            product=product,
            price=product.price * quantity,
            status="Pending",
            address=address,
            quantity=quantity

        )

        # Stock update
        product.stock -= quantity
        product.save()

        return Response({
            "message": "Order placed successfully",
            "order_id": order.id
        }, status=status.HTTP_201_CREATED)
    
    def delete(self, request):
        order_id = request.data.get("id")
        try:
            order = Order.objects.get(id=order_id, user=request.user)
            order.status = 'cancelled'
            order.save()
            return Response({"message": "Order cancelled successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

class manageOrderAPIView(APIView):
    permission_classes = [IsStaffUser]

    def get(self, request):
        orders = Order.objects.all()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        order_id = request.data.get("id")
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = OrderSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            order = serializer.save()
            return Response({"message": "Order updated successfully", "order_id": order.id}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReviewAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        order_id = request.data.get("order")
        rating = request.data.get("rating")
        comment = request.data.get("comment")

        # Order exist check
        order = Order.objects.filter(id=order_id, user=request.user).first()
        if not order:
            return Response({"error": "Order not found or does not belong to the user"}, status=status.HTTP_404_NOT_FOUND)
        
        
        # Create the review
        review_instance = review.objects.create(
            product=order.product,
            user=request.user,
            order=order.id,
            rating=rating,
            comment=comment
        )

        serializer = ReviewSerializer(review_instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
class ReviewListAPIView(APIView):
    def get(self, request,pk):
        """List all reviews for a product"""
        reviews = review.objects.filter(product_id=pk)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
