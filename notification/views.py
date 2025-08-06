from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import *

class UserNotificationsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifications = Notification.objects.filter(user=request.user)
        serializer = NotificationSerializer(notifications, many=True)
        return Response({"status": "success", "data": serializer.data}, status=200)
    
class UserNotificationsMarkAsReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk=None):
        try:
            notification = Notification.objects.get(id=pk, user=request.user)
            notification.is_read = True
            notification.save()
            return Response({"status": "success", "message": "Notification marked as read"}, status=200)
        except Notification.DoesNotExist:
            return Response({"status": "error", "message": "Notification not found"}, status=404)
        
class UserNotificationsMarkAllAsReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        notifications = Notification.objects.filter(user=request.user, is_read=False)
        notifications.update(is_read=True)
        return Response({"status": "success", "message": "All notifications marked as read"}, status=200)
    

class AdminNotificationsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            if not request.user.is_superuser:
                return Response({"status": "error", "message": "Permission denied"}, status=403)
            admin_notifications = AdminNotification.objects.all().order_by('-created_at')
            serializer = AdminNotificationSerializer(admin_notifications, many=True)
            return Response({"status": "success", "data": serializer.data}, status=200)
        except AdminNotification.DoesNotExist:
            return Response({"status": "error", "message": "No notifications found"}, status=404)
        

class AdminNotificationsMarkAsReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk=None):
        try:
            if not request.user.is_superuser:
                return Response({"status": "error", "message": "Permission denied"}, status=403)
            notification = AdminNotification.objects.get(id=pk)
            notification.is_read = True
            notification.save()
            return Response({"status": "success", "message": "Notification marked as read"}, status=200)
        except AdminNotification.DoesNotExist:
            return Response({"status": "error", "message": "Notification not found"}, status=404)
class AdminNotificationsMarkAllAsReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not request.user.is_superuser:
            return Response({"status": "error", "message": "Permission denied"}, status=403)
        admin_notifications = AdminNotification.objects.filter(is_read=False)
        admin_notifications.update(is_read=True)
        return Response({"status": "success", "message": "All notifications marked as read"}, status=200)

