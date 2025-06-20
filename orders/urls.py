from django.urls import path, include
from .views import *

urlpatterns = [
    path('orders/', OrderViewSet.as_view(), name='order_list'),
    path('orders/<int:pk>/', OrderViewSet.as_view(), name='order_detail'),
    path('order_items/', OrderItemViewSet.as_view(), name='order_item_list'),
    path('order_items/<int:pk>/', OrderItemViewSet.as_view(), name='order_item_detail'),


    path('pending_order/', PendingOrderViewSet.as_view(), name='pending_order'),


    path('return/request/<int:order_item_id>/', ReturnRequestAPIView.as_view(), name='return_request'),
    path('return/process/<int:return_id>/', ReturnProcessAPIView.as_view(), name='return_process'),
]
