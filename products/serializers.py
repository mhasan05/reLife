from rest_framework import serializers
from .models import *

class ProductSerializer(serializers.ModelSerializer):
    generic_name = serializers.PrimaryKeyRelatedField(
        queryset=GenericName.objects.all()
    )
    cost_price = serializers.FloatField()
    mrp = serializers.FloatField()
    selling_price = serializers.FloatField()
    discount_percent = serializers.FloatField()
    category_name = serializers.SerializerMethodField()
    company_name = serializers.ReadOnlyField(source='company_id.company_name')

    class Meta:
        model = Product
        fields = [
            'product_id', 'product_name','generic_name', 'product_description', 'product_image',
            'sku','quantity_per_box', 'company_id','company_name', 'category_id', 'category_name', 'stock_quantity','cost_price',
            'mrp','selling_price', 'discount_percent', 'out_of_stock', 'is_active', 'created_on', 'updated_on'
        ]


    def discount_percent(self, obj):
        return obj.discountPercentage()

    def get_category_name(self, obj):
        """
        Returns a list of category names associated with the product.
        """
        return [category.name for category in obj.category_id.all()]
        
    def to_representation(self, instance):
        """Show generic_name as its `name` instead of ID"""
        rep = super().to_representation(instance)
        if instance.generic_name:
            rep['generic_name'] = instance.generic_name.name  # ✅ use GenericName.name
        return rep
    
class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Product.company_id.field.related_model
        fields = ['company_id', 'company_name', 'logo','is_active', 'created_on', 'updated_on']

class ProductNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['product_name']  # only include product_name

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Product.category_id.field.related_model
        fields = ['category_id', 'name', 'description','is_active', 'created_on', 'updated_on']

class GenericNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = GenericName
        fields = ['generic_id', 'name', 'description', 'created_on', 'updated_on']

class ProductNameListSerializer(serializers.ModelSerializer):
    class Meta:
        model = GenericName
        fields = ['name']  # only include name
class BannerImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BannerImages
        fields = '__all__'



class GetTempProductBatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = TempProduct
        fields = ['batch_id']