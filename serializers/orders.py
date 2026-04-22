from rest_framework import serializers
from models.orders import Cart, CartItem, Order, OrderItem
from serializers.products import ProductListSerializer


class AddToCartSerializer(serializers.Serializer):
    """Serializer for adding products to cart"""
    product_id = serializers.IntegerField(required=True, help_text="ID of the product to add")
    quantity = serializers.IntegerField(default=1, min_value=1, help_text="Quantity to add (default: 1)")


class UpdateCartItemSerializer(serializers.Serializer):
    """Serializer for updating cart item quantity"""
    quantity = serializers.IntegerField(required=True, min_value=1, help_text="New quantity for the item")


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    subtotal = serializers.ReadOnlyField()
    
    class Meta:
        model = CartItem
        fields = ('id', 'product', 'product_id', 'quantity', 'subtotal', 'added_at')
        read_only_fields = ('id', 'added_at')


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_amount = serializers.ReadOnlyField()
    total_items = serializers.ReadOnlyField()
    
    class Meta:
        model = Cart
        fields = ('id', 'user', 'items', 'total_amount', 'total_items', 'created_at', 'updated_at')
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    subtotal = serializers.ReadOnlyField()
    
    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'quantity', 'price_at_purchase', 'subtotal')


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = ('id', 'order_number', 'status', 'total_amount', 'shipping_address', 
                 'shipping_city', 'shipping_pincode', 'shipping_phone', 'items', 'created_at', 'updated_at')
        read_only_fields = ('id', 'order_number', 'status', 'total_amount', 'created_at', 'updated_at')


class OrderCreateSerializer(serializers.Serializer):
    shipping_address = serializers.CharField(max_length=500, required=True, help_text="Full shipping address")
    shipping_city = serializers.CharField(max_length=100, required=True, help_text="City name")
    shipping_pincode = serializers.CharField(max_length=10, required=True, help_text="Postal/ZIP code")  
    shipping_phone = serializers.CharField(max_length=15, required=True, help_text="Contact phone number")
