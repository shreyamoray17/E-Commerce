from rest_framework import serializers
from models.payments import Payment


class InitiatePaymentSerializer(serializers.Serializer):
    """Serializer for initiating payment"""
    order_id = serializers.IntegerField(required=True, help_text="ID of the order to pay for")
    payment_method = serializers.ChoiceField(
        choices=['credit_card', 'debit_card', 'upi', 'net_banking'],
        required=True,
        help_text="Payment method"
    )


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ('id', 'order', 'payment_method', 'transaction_id', 'amount', 'status', 'payment_date', 'created_at')
        read_only_fields = ('id', 'transaction_id', 'created_at')


class PaymentInitiateSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    payment_method = serializers.ChoiceField(choices=Payment.PAYMENT_METHOD_CHOICES, default='mock')
