from rest_framework import serializers
from .models import Order, OrderItem, Return
from products.models import Product
from django.utils import timezone
from accounts.models import UserAuth

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.product_name', read_only=True)
    discount_percent = serializers.FloatField(source='product.discount_percent', read_only=True)
    discount = serializers.SerializerMethodField()
    mrp = serializers.FloatField(source='product.mrp', read_only=True)
    selling_price = serializers.FloatField(source='product.selling_price', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id','product', 'product_name', 'quantity', 'mrp','selling_price', 'discount_percent','discount', 'items_total','created_on', 'updated_on']
        # fields = '__all__'

    def validate_quantity(self, value):
        if value == 0:
            raise serializers.ValidationError("Quantity must be greater than zero.")
        return value
    
    def items_total(self, obj):
        """
        Calculates the total price for this item based on quantity and unit price.
        """
        return obj.unit_price * obj.quantity
    def get_discount(self, obj):
        """
        Retrieves the discount amount from the product's discount method.
        """
        return (obj.product.mrp - obj.product.selling_price) * obj.quantity

class OrderSerializer(serializers.ModelSerializer):
    delivery_charge = serializers.FloatField()  # force as number
    items = OrderItemSerializer(many=True)
    total_amount = serializers.SerializerMethodField()
    final_amount = serializers.SerializerMethodField()  # New field
    shipping_address = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Order
        fields = ['order_id','invoice_number', 'user_id', 'total_amount','delivery_charge','final_amount', 'shipping_address', 'order_status', 'order_date', 'items']

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])

        user = validated_data.get('user_id')
        if user and hasattr(user, 'shop_address'):
            validated_data['shipping_address'] = user.shop_address

        # Temporarily create order without total_amount
        order = Order.objects.create(**validated_data)

        # Create order items and calculate total
        total_amount = 0
        for item_data in items_data:
            product = Product.objects.select_for_update().get(pk=item_data['product'].pk)
            quantity = item_data['quantity']

            if product.stock_quantity < quantity:
                raise serializers.ValidationError({
                    'product': f"Not enough stock for {product.product_name}."
                })

            product.stock_quantity -= quantity
            product.save()
            
            order_item = OrderItem.objects.create(order=order, **item_data)
            total_amount += order_item.items_total()

        # Update total_amount and save order
        order.total_amount = total_amount
        order.save()

        return order
    
    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)

        # Update order fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        order = instance
        if items_data is not None:
            # Remove existing items (or implement partial update logic if needed)
            instance.items.all().delete()

            # Create new items from incoming data
            total_amount = 0
            for item_data in items_data:
                order_item = OrderItem.objects.create(order=order, **item_data)
                total_amount += order_item.items_total()

            # Update total_amount and save order
            order.total_amount = total_amount
            order.save()

        return order

    def get_total_amount(self, obj):
        # Sum the total for all related OrderItems
        return sum(item.items_total() for item in obj.items.all())
    def get_final_amount(self, obj):
        return float(obj.total_amount) + float(obj.delivery_charge)
    def get_shipping_address(self, obj):
        return obj.user_id.shop_address if obj.user_id and obj.user_id.shop_address else None





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

