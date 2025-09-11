from django.urls import path, include
from .views import *

urlpatterns = [
    path('orders/', OrderViewSet.as_view(), name='order_list'),
    path('orders/<int:pk>/', OrderViewSet.as_view(), name='order_detail'),
    path('order_items/', OrderItemViewSet.as_view(), name='order_item_list'),
    path('order_items/<int:pk>/', OrderItemViewSet.as_view(), name='order_item_detail'),
    path('pending_order/', PendingOrderViewSet.as_view(), name='pending_order'),
]
