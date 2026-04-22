from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from models.payments import Payment
from models.orders import Order
from serializers.payments import PaymentSerializer, PaymentInitiateSerializer
import uuid


@swagger_auto_schema(
    method='post',
    request_body=PaymentInitiateSerializer,
    responses={
        200: PaymentSerializer,
        400: 'Bad Request - Order already paid',
        404: 'Order not found'
    },
    operation_description="Initiate payment for an order (Mock payment - always succeeds)"
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_payment(request):
    serializer = PaymentInitiateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    order_id = serializer.validated_data['order_id']
    payment_method = serializer.validated_data.get('payment_method', 'mock')
    
    # Get order
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Check if payment already exists
    if hasattr(order, 'payment'):
        if order.payment.status == 'success':
            return Response({'error': 'Payment already completed'}, status=status.HTTP_400_BAD_REQUEST)
        # Delete old pending payment
        order.payment.delete()
    
    # Create payment
    transaction_id = f'TXN-MOCK-{uuid.uuid4().hex[:12].upper()}'
    
    payment = Payment.objects.create(
        order=order,
        payment_method=payment_method,
        transaction_id=transaction_id,
        amount=order.total_amount,
        status='pending'
    )
    
    # Mock payment processing - automatically succeed
    payment.status = 'success'
    payment.payment_date = timezone.now()
    payment.save()
    
    # Update order status
    order.status = 'paid'
    order.save()
    
    return Response({
        'message': 'Payment successful (simulated)',
        'payment': PaymentSerializer(payment).data,
        'order_status': order.status
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_payment_status(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if not hasattr(order, 'payment'):
        return Response({'error': 'Payment not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = PaymentSerializer(order.payment)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def simulate_payment_failure(request):
    """
    Endpoint to simulate payment failure for testing purposes
    """
    serializer = PaymentInitiateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    order_id = serializer.validated_data['order_id']
    payment_method = serializer.validated_data.get('payment_method', 'mock')
    
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Check if payment already exists
    if hasattr(order, 'payment'):
        if order.payment.status == 'success':
            return Response({'error': 'Payment already completed'}, status=status.HTTP_400_BAD_REQUEST)
        order.payment.delete()
    
    transaction_id = f'TXN-MOCK-{uuid.uuid4().hex[:12].upper()}'
    
    payment = Payment.objects.create(
        order=order,
        payment_method=payment_method,
        transaction_id=transaction_id,
        amount=order.total_amount,
        status='failed'
    )
    
    return Response({
        'message': 'Payment failed (simulated)',
        'payment': PaymentSerializer(payment).data
    }, status=status.HTTP_200_OK)
