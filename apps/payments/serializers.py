from rest_framework import serializers
from .models import Payment, Payout


class PaymentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'booking', 'user', 'user_name',
            'amount', 'method', 'status',
            'paystack_reference', 'paystack_access_code',
            'paid_at', 'created_at'
        ]
        read_only_fields = ['user', 'status', 'paystack_reference', 'paystack_access_code', 'paid_at']


class PayoutSerializer(serializers.ModelSerializer):
    host_name = serializers.CharField(source='host.get_full_name', read_only=True)

    class Meta:
        model = Payout
        fields = [
            'id', 'host', 'host_name', 'booking',
            'amount', 'platform_fee', 'net_amount', 'status',
            'completed_at', 'created_at'
        ]
        read_only_fields = ['status', 'platform_fee', 'net_amount', 'completed_at']