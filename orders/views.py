from rest_framework import viewsets
from .models import Order, OrderItem, Return
from .serializers import OrderSerializer, OrderItemSerializer,ReturnSerializer, ReturnProcessSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

class OrderViewSet(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        user = request.user
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
        serializer = OrderSerializer(orders, many=True)
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"status": "error", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk=None):
        try:
            order = Order.objects.get(pk=pk)
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





class ReturnRequestAPIView(APIView):
    """
    Handle creation of return requests.
    """

    def post(self, request, order_item_id):
        order_item = OrderItem.objects.filter(id=order_item_id).first()
        if not order_item:
            return Response({"error": "Order item not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ReturnSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(order_item=order_item)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ReturnProcessAPIView(APIView):
    """
    Handle processing of return requests (approve/reject).
    """

    def post(self, request, return_id):
        return_instance = Return.objects.filter(id=return_id).first()
        if not return_instance:
            return Response({"error": "Return request not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ReturnProcessSerializer(return_instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
