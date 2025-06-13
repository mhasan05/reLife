from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    discount = serializers.SerializerMethodField()
    selling_price = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()
    company_name = serializers.ReadOnlyField(source='company_id.company_name')

    class Meta:
        model = Product
        fields = [
            'product_id', 'product_name', 'product_description', 'product_image',
            'sku', 'company_id','company_name', 'category_id', 'category_name', 'stock_quantity', 'discount_percent','cost_price',
            'mrp', 'out_of_stock', 'is_active', 'created_on', 'updated_on',
            'discount', 'selling_price'
        ]

    def discount(self, obj):
        return obj.discount()

    def selling_price(self, obj):
        return obj.selling_price()
    
    def get_category_name(self, obj):
        """
        Returns a list of category names associated with the product.
        """
        return [category.name for category in obj.category_id.all()]
    
class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Product.company_id.field.related_model
        fields = ['company_id', 'company_name', 'logo','is_active', 'created_on', 'updated_on']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Product.category_id.field.related_model
        fields = ['category_id', 'name', 'description', 'created_on', 'updated_on']

