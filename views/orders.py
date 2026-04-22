from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from models.orders import Cart, CartItem, Order, OrderItem
from models.products import Product
from serializers.orders import (
    CartSerializer, CartItemSerializer, OrderSerializer, 
    OrderCreateSerializer, AddToCartSerializer
)
import uuid
from decimal import Decimal


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    serializer = CartSerializer(cart)
    return Response(serializer.data)


@swagger_auto_schema(
    method='post',
    request_body=AddToCartSerializer,
    responses={
        200: CartSerializer,
        400: 'Bad Request - Invalid data or insufficient stock',
        401: 'Unauthorized - Authentication required'
    },
    operation_description="Add a product to your shopping cart. Provide product_id and quantity."
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_cart(request):
    """
    Add a product to cart
    
    Request body:
    {
        "product_id": 1,
        "quantity": 2
    }
    """
    from serializers.orders import AddToCartSerializer
    
    serializer = AddToCartSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    product_id = serializer.validated_data['product_id']
    quantity = serializer.validated_data['quantity']
    
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    if product.stock_quantity < quantity:
        return Response({'error': 'Not enough stock'}, status=status.HTTP_400_BAD_REQUEST)
    
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': quantity}
    )
    
    if not created:
        cart_item.quantity += quantity
        if cart_item.quantity > product.stock_quantity:
            return Response({'error': 'Not enough stock'}, status=status.HTTP_400_BAD_REQUEST)
        cart_item.save()
    
    # Return full cart instead of just the item
    cart_serializer = CartSerializer(cart)
    return Response(cart_serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='patch',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['quantity'],
        properties={
            'quantity': openapi.Schema(type=openapi.TYPE_INTEGER, description='New quantity', minimum=1)
        }
    ),
    responses={
        200: CartSerializer,
        400: 'Bad Request',
        404: 'Cart item not found'
    },
    operation_description="Update quantity of an item in your cart"
)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_cart_item(request, item_id):
    """
    Update cart item quantity
    
    Request body:
    {
        "quantity": 5
    }
    """
    from serializers.orders import UpdateCartItemSerializer
    
    serializer = UpdateCartItemSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    quantity = serializer.validated_data['quantity']
    
    cart = get_object_or_404(Cart, user=request.user)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    
    if cart_item.product.stock_quantity < quantity:
        return Response({'error': 'Not enough stock'}, status=status.HTTP_400_BAD_REQUEST)
    
    cart_item.quantity = quantity
    cart_item.save()
    
    # Return full cart
    cart_serializer = CartSerializer(cart)
    return Response(cart_serializer.data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_from_cart(request, item_id):
    cart = get_object_or_404(Cart, user=request.user)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    cart_item.delete()
    return Response({'message': 'Item removed from cart'}, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='post',
    request_body=OrderCreateSerializer,
    responses={
        201: OrderSerializer,
        400: 'Bad Request - Cart empty or insufficient stock',
        401: 'Unauthorized'
    },
    operation_description="Create an order from your cart items. Provide shipping details."
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@transaction.atomic
def create_order(request):
    """
    Create order from cart
    
    Request body:
    {
        "shipping_address": "123 Main Street",
        "shipping_city": "Mumbai",
        "shipping_state": "Maharashtra",
        "shipping_zip_code": "400001"
    }
    """
    serializer = OrderCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.items.all()
    
    if not cart_items:
        return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Check stock availability
    for item in cart_items:
        if item.product.stock_quantity < item.quantity:
            return Response({
                'error': f'Not enough stock for {item.product.name}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    # Calculate total
    total_amount = sum(item.subtotal for item in cart_items)
    
    # Create order
    order = Order.objects.create(
        user=request.user,
        order_number=f'ORD-{uuid.uuid4().hex[:10].upper()}',
        total_amount=total_amount,
        **serializer.validated_data
    )
    
    # Create order items and update stock
    for cart_item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=cart_item.product,
            quantity=cart_item.quantity,
            price_at_purchase=cart_item.product.price
        )
        
        # Reduce stock
        cart_item.product.stock_quantity -= cart_item.quantity
        cart_item.product.save()
    
    # Clear cart
    cart_items.delete()
    
    order_serializer = OrderSerializer(order)
    return Response(order_serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_orders(request):
    orders = Order.objects.filter(user=request.user)
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    serializer = OrderSerializer(order)
    return Response(serializer.data)
