from rest_framework import serializers
from .models import Order, OrderItem, Return
from products.models import Product
from django.utils import timezone

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_amount = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['order_id', 'user_id', 'total_amount', 'shipping_address', 'order_status', 'order_date', 'items']

    def get_total_amount(self, obj):
        return obj.get_total_price()
    



class ReturnSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='order_item.product.product_name')
    order_id = serializers.ReadOnlyField(source='order_item.order.order_id')

    class Meta:
        model = Return
        fields = ['return_id', 'order_item', 'order_id', 'product_name', 'quantity', 'reason', 'status', 'created_on', 'processed_on', 'processed_by']
        read_only_fields = ['status', 'created_on', 'processed_on', 'processed_by']

    def validate(self, data):
        """
        Validate return quantity does not exceed ordered quantity.
        """
        order_item = data['order_item']
        if data['quantity'] > order_item.quantity:
            raise serializers.ValidationError("Return quantity exceeds the ordered quantity.")
        return data

    def create(self, validated_data):
        """
        Create a new return request.
        """
        return Return.objects.create(**validated_data)

class ReturnProcessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Return
        fields = ['status', 'processed_by']

    def update(self, instance, validated_data):
        """
        Update the status of a return request.
        """
        instance.status = validated_data.get('status', instance.status)
        instance.processed_by = validated_data.get('processed_by', instance.processed_by)

        if instance.status == 'approved':
            if instance.is_valid_return():
                instance.process_return()
            else:
                raise serializers.ValidationError("Return quantity is invalid.")

        instance.processed_on = timezone.now()
        instance.save()
        return instance

