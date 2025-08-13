from rest_framework import serializers
from .models import Order


class OrderSerializer(serializers.ModelSerializer):
    # Flattened fields (no nested product object)
    order_id = serializers.IntegerField(source='id', read_only=True)
    product_id = serializers.IntegerField(source='product.id', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    unit_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)
    line_total = serializers.DecimalField(source='price', max_digits=10, decimal_places=2, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Order
        fields = (
            'order_id',
            'product_id',
            'product_name',
            'quantity',
            'unit_price',
            'line_total',
            'address',
            'status',
            'status_display',
            'created_at',
        )
        read_only_fields = (
            'order_id',
            'product_id',
            'product_name',
            'quantity',
            'unit_price',
            'line_total',
            'address',
            'status',
            'status_display',
            'created_at',
        )


class OrderCreateSerializer(serializers.Serializer):
    """Write payload for creating an order (used by POST)."""
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)
    address = serializers.CharField(max_length=500)

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1.")
        return value
