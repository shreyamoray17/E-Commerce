from rest_framework import status, generics, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.core.cache import cache
from models.products import Product
from serializers.products import ProductSerializer, ProductListSerializer
from utils.cache import (
    get_product_list_cache_key, get_product_detail_cache_key,
    cache_product_list, cache_product_detail, clear_product_cache
)
from utils.permissions import IsAdminOrReadOnly


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializer
        return ProductSerializer
    
    def list(self, request, *args, **kwargs):
        page = request.query_params.get('page', 1)
        try:
            page = int(page)
        except (ValueError, TypeError):
            page = 1
        
        # Try to get from cache
        cache_key = get_product_list_cache_key(page)
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)
        
        # If not in cache, get from database
        response = super().list(request, *args, **kwargs)
        
        # Cache the response
        cache_product_list(page, response.data, timeout=900)  # 15 minutes
        
        return response
    
    def retrieve(self, request, *args, **kwargs):
        product_id = kwargs.get('pk')
        
        # Try to get from cache
        cache_key = get_product_detail_cache_key(product_id)
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)
        
        # If not in cache, get from database
        response = super().retrieve(request, *args, **kwargs)
        
        # Cache the response
        cache_product_detail(product_id, response.data, timeout=1800)  # 30 minutes
        
        return response
    
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        # Clear product list cache when new product is added
        clear_product_cache()
        return response
    
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        product_id = kwargs.get('pk')
        # Clear specific product cache and list cache
        clear_product_cache(product_id)
        return response
    
    def destroy(self, request, *args, **kwargs):
        product_id = kwargs.get('pk')
        response = super().destroy(request, *args, **kwargs)
        # Clear specific product cache and list cache
        clear_product_cache(product_id)
        return response
