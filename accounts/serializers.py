from rest_framework import serializers
from .models import UserAuth, Area, Address




class UserAuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAuth
        fields = ['user_id', 'full_name', 'email', 'phone', 'image', 'shop_name', 'default_address', 'area', 'is_approved', 'is_active', 'is_staff', 'is_superuser', 'date_joined', 'created_on', 'updated_on']




class UserAuthSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserAuth
        fields = [
            'user_id', 'full_name', 'email', 'phone', 'image', 'shop_name', 'default_address', 'area', 'is_approved', 'is_active', 'is_staff', 'is_superuser', 'date_joined', 'created_on', 'updated_on'
        ]





class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = '__all__'


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['address_id', 'user_id', 'full_name', 'phone', 'address', 'area', 'zip_code', 'is_default', 'created_on', 'updated_on']
