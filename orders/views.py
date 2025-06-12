from rest_framework import viewsets
from .models import Order, OrderItem, Return
from .serializers import OrderSerializer, OrderItemSerializer,ReturnSerializer, ReturnProcessSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer





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
