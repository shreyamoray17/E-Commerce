from rest_framework import serializers
from models.products import Product


class ProductSerializer(serializers.ModelSerializer):
    in_stock = serializers.ReadOnlyField()
    
    class Meta:
        model = Product
        fields = ('id', 'name', 'description', 'price', 'stock_quantity', 'image_url', 'is_active', 'in_stock', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class ProductListSerializer(serializers.ModelSerializer):
    in_stock = serializers.ReadOnlyField()
    
    class Meta:
        model = Product
        fields = ('id', 'name', 'price', 'stock_quantity', 'image_url', 'in_stock', 'is_active')
