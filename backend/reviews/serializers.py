from rest_framework import serializers
from .models import Review


class ReviewReadSerializer(serializers.ModelSerializer):
    # Flattened product info (no nested object)
    review_id = serializers.IntegerField(source='id', read_only=True)
    product_id = serializers.IntegerField(source='product.id', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    author = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Review
        fields = (
            'review_id', 'product_id', 'product_name',
            'rating', 'title', 'body',
            'is_verified_purchase',
            'status', 'status_display',
            'author',
            'created_at',
        )
        read_only_fields = fields

    def get_author(self, obj):
        # hide email etc., show username only if user exists
        return getattr(obj.user, 'username', None)


class ReviewCreateSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    rating = serializers.IntegerField(min_value=1, max_value=5)
    title = serializers.CharField(max_length=120, allow_blank=True, required=False)
    body = serializers.CharField(max_length=2000)

    def validate_rating(self, v):
        if not (1 <= v <= 5):
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return v
