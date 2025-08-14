# serializers.py
from rest_framework import serializers
from .models import Users, Category, Product, Order, review
from django.contrib.auth import authenticate
from django.utils.translation import gettext as _




class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['username', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = Users.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            is_active=True,   # API se create hone wale users ka active hoga
            is_staff=False    # Staff permission false
        )
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login
    """
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError(
                    {"error": _("Invalid username or password.")}
                )
        else:
            raise serializers.ValidationError(
                {"error": _("Both username and password are required.")}
            )

        attrs['user'] = user
        return attrs
    
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"
        
    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None



class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ['user', 'created_at']


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = review
        fields = "__all__"
        # read_only_fields = ['user', 'created_at']
    
