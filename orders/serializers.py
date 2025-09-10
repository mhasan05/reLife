from rest_framework import serializers
from .models import *
from products.models import Product
from django.utils import timezone
from accounts.models import UserAuth

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.product_name', read_only=True)
    product_image = serializers.ImageField(source='product.product_image', read_only=True, use_url=True)
    company_name = serializers.CharField(source='product.company_id', read_only=True)
    discount_percent = serializers.FloatField(source='product.discount_percent', read_only=True)
    discount = serializers.SerializerMethodField()
    mrp = serializers.FloatField(source='product.mrp', read_only=True)
    selling_price = serializers.FloatField(source='product.selling_price', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id','product', 'product_name','product_image','company_name', 'quantity', 'mrp','selling_price', 'discount_percent','discount', 'items_total','created_on', 'updated_on']
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
    
class ReturnItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product.product_name", read_only=True)
    product_image = serializers.ImageField(source='product.product_image', read_only=True, use_url=True)
    company_name = serializers.CharField(source='product.company_id', read_only=True)
    mrp = serializers.SerializerMethodField()
    selling_price = serializers.SerializerMethodField()
    discount_percent = serializers.SerializerMethodField()
    total_return = serializers.SerializerMethodField()

    class Meta:
        model = ReturnItem
        fields = [
            "id", "product", "product_name",'product_image','company_name', "quantity",
            "mrp", "selling_price", "discount_percent",
            "reason", "created_on", "updated_on",
            "total_return",
        ]

    def get_mrp(self, obj):
        return float(obj.product.mrp) if obj.product else 0.0

    def get_selling_price(self, obj):
        return float(obj.product.selling_price) if obj.product else 0.0

    def get_discount_percent(self, obj):
        return float(obj.product.discount_percent) if obj.product else 0.0

    def get_total_return(self, obj):
        return float(obj.quantity * obj.product.selling_price) if obj.product else 0.0


class OrderSerializer(serializers.ModelSerializer):
    delivery_charge = serializers.FloatField()  # ensure number
    items = OrderItemSerializer(many=True)
    return_items = ReturnItemSerializer(many=True, read_only=True)
    total_return_amount = serializers.SerializerMethodField()  # NEW field
    total_amount = serializers.SerializerMethodField()
    final_amount = serializers.SerializerMethodField()
    shipping_address = serializers.CharField(required=False, allow_blank=True)
    full_name = serializers.SerializerMethodField()  # NEW
    shop_name = serializers.SerializerMethodField()  # NEW

    class Meta:
        model = Order
        fields = [
            'order_id', 'invoice_number', 'user_id','full_name',
            'total_amount', 'delivery_charge', 'final_amount',
            'total_return_amount','shop_name', 'shipping_address',
            'order_status', 'order_date', 'items', 'return_items'
        ]


    # --------------------
    # Calculate total amount from order items
    # --------------------
    def get_total_amount(self, obj):
        total = sum([item.items_total() for item in obj.items.all()])
        return float(total)

    # --------------------
    # Final amount including delivery
    # --------------------
    def get_final_amount(self, obj):
        return self.get_total_amount(obj) + float(obj.delivery_charge or 0.0)
        
    def get_full_name(self, obj):
        return obj.user_id.full_name if obj.user_id else None
        
    def get_shop_name(self, obj):
        return obj.user_id.shop_name if obj.user_id else None

    # --------------------
    # Create order with items
    # --------------------
    def create(self, validated_data):
        items_data = validated_data.pop('items', [])

        # Set shipping_address from user if available
        user = validated_data.get('user_id')
        if user and hasattr(user, 'shop_address'):
            validated_data['shipping_address'] = user.shop_address

        # Temporarily create order
        order = Order.objects.create(**validated_data)

        # Create order items and calculate total
        total_amount = 0
        for item_data in items_data:
            product = Product.objects.select_for_update().get(pk=item_data['product'].pk)
            quantity = item_data['quantity']

            # if product.stock_quantity < quantity:
            #     raise serializers.ValidationError({
            #         'product': f"Not enough stock for {product.product_name}."
            #     })

            product.stock_quantity -= quantity
            product.save()

            order_item = OrderItem.objects.create(order=order, **item_data)
            total_amount += order_item.items_total()

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
        total_amt = sum(item.items_total() for item in obj.items.all())
        return float(total_amt) + float(obj.delivery_charge)
    
    def get_total_return_amount(self, obj):
        """Sum of all return item amounts"""
        total = 0
        for item in obj.return_items.all():
            total += float(item.quantity) * float(item.product.selling_price)
        return total
    
    def get_shipping_address(self, obj):
        return obj.user_id.shop_address if obj.user_id and obj.user_id.shop_address else None





