from decimal import Decimal, ROUND_HALF_UP
from django.db import transaction
from django.db.models import F
from rest_framework import permissions, status, generics
from rest_framework.response import Response
from rest_framework.views import APIView

from products.models import Product
from .models import Order
from .serializers import OrderSerializer, OrderCreateSerializer


def _money(x):
    # Normalize to two decimals with standard rounding
    return (Decimal(x).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))


class OrderListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/orders/      -> list authenticated user's orders
    POST /api/orders/      -> create an order (server-calculated price)
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).select_related('product').order_by('-created_at')

    def get_serializer_class(self):
        return OrderCreateSerializer if self.request.method == 'POST' else OrderSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        # Validate input payload
        write_ser = OrderCreateSerializer(data=request.data)
        write_ser.is_valid(raise_exception=True)
        product_id = write_ser.validated_data['product_id']
        qty = write_ser.validated_data['quantity']
        address = write_ser.validated_data['address']

        # Optional idempotency (send Idempotency-Key header from client)
        idem_key = request.headers.get('Idempotency-Key') or None
        if idem_key:
            existing = Order.objects.filter(user=request.user, idempotency_key=idem_key).first()
            if existing:
                return Response(
                    {"message": "Order already created", "order_id": existing.id},
                    status=status.HTTP_200_OK
                )

        # Lock the product row to avoid race conditions on stock
        product = (Product.objects
                   .select_for_update()
                   .filter(id=product_id)
                   .first())
        if not product:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        # Ensure stock is sufficient
        # If your Product has 'stock' field different, adjust here.
        if getattr(product, 'stock', 0) < qty:
            return Response({"error": "Not enough stock"}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate server-side price
        unit_price = _money(product.price)
        order_total = _money(unit_price * qty)

        # Decrement stock atomically
        Product.objects.filter(id=product.id).update(stock=F('stock') - qty)

        # Create order (status starts as 'pending')
        order = Order.objects.create(
            user=request.user,
            product=product,
            price=order_total,    # final total stored
            quantity=qty,
            address=address,
            status=Order.Status.PENDING,
            idempotency_key=idem_key,
        )

        return Response(
            {"message": "Order placed successfully", "order_id": order.id},
            status=status.HTTP_201_CREATED
        )


class OrderDetailView(APIView):
    """
    DELETE /api/orders/<pk>/      -> delete an order you own (hard delete)
    PATCH  /api/orders/<pk>/cancel -> cancel a pending order and restock
    """
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        order = Order.objects.filter(pk=pk, user=request.user).first()
        if not order:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        order.delete()
        return Response({"message": "Order deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

    @transaction.atomic
    def patch(self, request, pk):
        action = request.query_params.get('action')
        if action != 'cancel':
            return Response({"error": "Unsupported action"}, status=status.HTTP_400_BAD_REQUEST)

        order = (Order.objects
                 .select_for_update()
                 .filter(pk=pk, user=request.user)
                 .first())
        if not order:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        if order.status != Order.Status.PENDING:
            return Response({"error": "Only pending orders can be cancelled"}, status=status.HTTP_400_BAD_REQUEST)

        # Restock product
        Product.objects.filter(id=order.product_id).update(stock=F('stock') + order.quantity)
        order.status = Order.Status.CANCELLED
        order.save(update_fields=['status'])

        return Response({"message": "Order cancelled and stock restored"}, status=status.HTTP_200_OK)
