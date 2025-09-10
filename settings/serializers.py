# serializers.py
from rest_framework import serializers
from .models import SiteInfoModel

class SiteInfoSerializer(serializers.ModelSerializer):
    delivery_charge = serializers.FloatField()  # force as number
    class Meta:
        model = SiteInfoModel
        fields = ['name', 'logo', 'description', 'version', 'delivery_charge', 'contact_email', 'contact_phone']
