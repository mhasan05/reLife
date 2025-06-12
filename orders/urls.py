from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, OrderItemViewSet,ReturnRequestAPIView, ReturnProcessAPIView

router = DefaultRouter()
router.register(r'orders', OrderViewSet)
router.register(r'orderitems', OrderItemViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('return/request/<int:order_item_id>/', ReturnRequestAPIView.as_view(), name='return_request'),
    path('return/process/<int:return_id>/', ReturnProcessAPIView.as_view(), name='return_process'),
]
