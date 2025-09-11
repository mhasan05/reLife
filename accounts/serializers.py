from rest_framework import serializers
from .models import *




class UserAuthSerializer(serializers.ModelSerializer):
    area_name = serializers.CharField(source='area.area_name', read_only=True)
    password = serializers.CharField(write_only=True, required=False)
    class Meta:
        model = UserAuth
        fields = ['user_id', 'full_name', 'email', 'phone', 'image', 'shop_name', 'shop_address', 'area','area_name', 'password', 'is_approved', 'is_active', 'is_staff', 'is_superuser', 'date_joined', 'created_on', 'updated_on']
        read_only_fields = ['date_joined', 'created_on', 'updated_on']

    def update(self, instance, validated_data):
        # Handle password separately
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)  # hashes the password correctly

        instance.save()
        return instance

class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = '__all__'

class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = '__all__'


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['address_id', 'user_id', 'full_name', 'phone', 'address', 'area', 'zip_code', 'is_default', 'created_on', 'updated_on']
