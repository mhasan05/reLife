from rest_framework import serializers
from .models import *

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'

class AdminNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminNotification
        fields = '__all__'
