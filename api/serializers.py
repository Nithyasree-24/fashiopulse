from rest_framework import serializers
from .models import User, Clothing, Order, Cart, Wishlist
from datetime import timedelta

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}

class ClothingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clothing
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    product_details = ClothingSerializer(source='product', read_only=True)
    expected_delivery_date = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = '__all__'

    def get_expected_delivery_date(self, obj):
        # Deterministic: (order_id % 5 + 2) gives 2 to 6 days
        days_to_add = (obj.order_id % 5) + 2
        delivery_date = obj.created_at + timedelta(days=days_to_add)
        return delivery_date.strftime("%d %b %Y")

class CartSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.product_name', read_only=True)
    product_image = serializers.CharField(source='product.product_image', read_only=True)
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)
    product_category = serializers.CharField(source='product.product_category', read_only=True)
    product_description = serializers.CharField(source='product.product_description', read_only=True)
    color = serializers.CharField(source='product.color', read_only=True)
    stock = serializers.IntegerField(source='product.stock', read_only=True)

    class Meta:
        model = Cart
        fields = '__all__'

class WishlistSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.product_name', read_only=True)
    product_image = serializers.CharField(source='product.product_image', read_only=True)
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)
    product_category = serializers.CharField(source='product.product_category', read_only=True)
    product_description = serializers.CharField(source='product.product_description', read_only=True)
    color = serializers.CharField(source='product.color', read_only=True)
    stock = serializers.IntegerField(source='product.stock', read_only=True)

    class Meta:
        model = Wishlist
        fields = '__all__'
