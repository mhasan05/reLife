from rest_framework import viewsets
from .models import *
from .serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from settings.models import SiteInfoModel
from notification.models import *
from django.utils.dateparse import parse_datetime


class OrderPagination(PageNumberPagination):
    page_size = 10  # default page size
    page_size_query_param = 'page_size'  # let client override page size using ?page_size=
    max_page_size = 500

class OrderViewSet(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = OrderPagination()

    def get(self, request, pk=None):
        user = request.user
        from_datetime = request.query_params.get('from_datetime')
        to_datetime = request.query_params.get('to_datetime')
        area = request.query_params.get('area')
        if from_datetime and to_datetime and area:
            # Parse ISO 8601 datetime strings
            from_dt = parse_datetime(from_datetime)
            to_dt = parse_datetime(to_datetime)

            # Filter orders by datetime and area
            orders = Order.objects.filter(
                order_date__range=(from_dt, to_dt),
                user_id__area_id=area
            )
            # Apply pagination
            paginator = self.pagination_class
            paginated_orders = paginator.paginate_queryset(orders, request)
            serializer = OrderSerializer(orders, many=True)
            return paginator.get_paginated_response({
                "status": "success",
                "data": serializer.data
            })
        if pk:
            try:
                order = Order.objects.get(pk=pk)
                serializer = OrderSerializer(order)
                return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
            except Order.DoesNotExist:
                return Response({"status": "error", "message": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        if user.is_superuser:
            orders = Order.objects.all().order_by('-created_on')
        else:
            orders = Order.objects.filter(user_id=user).order_by('-created_on')
        # Apply pagination
        paginator = self.pagination_class
        paginated_orders = paginator.paginate_queryset(orders, request)
        serializer = OrderSerializer(orders, many=True)
        return paginator.get_paginated_response({
            "status": "success",
            "data": serializer.data
        })

    def post(self, request):
        # Get delivery_charge from SiteInfoModel (fallback to 0 if not found)
        user = request.user
        site_info = SiteInfoModel.objects.first()
        delivery_charge = site_info.delivery_charge if site_info else 0
        district_name = None
        if user.area and user.area.district:
            district_name = str(user.area.district.name)

        # Add delivery_charge to the request data before serialization
        data = request.data.copy()
        if district_name and district_name.lower() == 'dhaka':
            data['delivery_charge'] = 0
        else:
            data['delivery_charge'] = delivery_charge
        serializer = OrderSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            # Create a notification for the admin
            admin_notification = AdminNotification.objects.create(
                user=request.user,
                title='New Order Created',
                order_id=serializer.instance,
                message=f"{request.user.full_name} has created a new order."
            )
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"status": "error", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk=None):
        try:
            order = Order.objects.get(pk=pk)
            customer = order.user_id
            if 'order_status' in request.data:
                # If status is being updated, create a notification
                Notification.objects.create(
                    title ='Order Update',
                    user=customer,
                    message=f"Your order {order.invoice_number} has been {request.data['order_status']}"
                )
            serializer = OrderSerializer(order, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
            return Response({"status": "error", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Order.DoesNotExist:
            return Response({"status": "error", "message": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk=None):
        try:
            order = Order.objects.get(pk=pk)
            order.delete()
            return Response({"status": "success", "message": "Order deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Order.DoesNotExist:
            return Response({"status": "error", "message": "Order not found"}, status=status.HTTP_404_NOT_FOUND)


class PendingOrderViewSet(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.is_superuser:
            orders = Order.objects.filter(order_status='pending').order_by('-created_on')
            pending_orders = Order.objects.filter(order_status='pending').order_by('-created_on').count()
        else:
            orders = Order.objects.filter(order_status='pending',user_id=user).order_by('-created_on')
            pending_orders = Order.objects.filter(order_status='pending',user_id=user).order_by('-created_on').count()
        serializer = OrderSerializer(orders, many=True)
        return Response({"status": "success",'total':pending_orders, "data": serializer.data}, status=status.HTTP_200_OK)


class OrderItemViewSet(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        user = request.user
        if pk:
            try:
                order_item = OrderItem.objects.get(pk=pk)
                serializer = OrderItemSerializer(order_item)
                return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
            except OrderItem.DoesNotExist:
                return Response({"status": "error", "message": "Order item not found"}, status=status.HTTP_404_NOT_FOUND)
        if user.is_superuser:
            order_items = OrderItem.objects.all().order_by('-created_on')
        else:
            order_items = OrderItem.objects.filter(user_id=user).order_by('-created_on')

        
        serializer = OrderItemSerializer(order_items, many=True)
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = OrderItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"status": "error", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk=None):
        try:
            order_item = OrderItem.objects.get(pk=pk)
            serializer = OrderItemSerializer(order_item, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
            return Response({"status": "error", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except OrderItem.DoesNotExist:
            return Response({"status": "error", "message": "Order item not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk=None):
        try:
            order_item = OrderItem.objects.get(pk=pk)
            order_item.delete()
            return Response({"status": "success", "message": "Order item deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except OrderItem.DoesNotExist:
            return Response({"status": "error", "message": "Order item not found"}, status=status.HTTP_404_NOT_FOUND)
        

