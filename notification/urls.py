# urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path('notifications/', UserNotificationsView.as_view(), name='notifications'),
    path('notifications/mark_as_read/<int:pk>/', UserNotificationsMarkAsReadView.as_view(), name='mark_notification_as_read'),
    path('notifications/mark_all_as_read/', UserNotificationsMarkAllAsReadView.as_view(), name='mark_all_notifications_as_read'),


    path('admin_notifications/', AdminNotificationsView.as_view(), name='admin_notifications'),
    path('admin_notifications/mark_as_read/<int:pk>/', AdminNotificationsMarkAsReadView.as_view(), name='mark_admin_notification_as_read'),
    path('admin_notifications/mark_all_as_read/', AdminNotificationsMarkAllAsReadView.as_view(), name='mark_all_admin_notifications_as_read'),
]
