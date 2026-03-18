from rest_framework import serializers
from .models import Order


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'id', 'customer_id', 'total_price', 'address',
            'payment_method', 'shipping_method', 'status', 'created_at'
        ]
        read_only_fields = ['id', 'status', 'created_at']
