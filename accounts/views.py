from rest_framework import viewsets
from .models import UserAuth, Area, Address
from .serializers import UserAuthSerializer, AreaSerializer, AddressSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate




class LoginView(APIView):
    """
    Handle user login.
    """
    def post(self, request):
        phone = request.data.get('phone')
        password = request.data.get('password')

        if not phone or not password:
            return Response({'status': 'error',"message": "Both phone and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, phone=phone, password=password)

        if user is None:
            return Response({'status': 'error', "message": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)


        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        return Response({
            'status': 'success',
            'access_token': str(access_token),
            'data': UserAuthSerializer(user).data
        }, status=status.HTTP_200_OK)



class CustomerView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            try:
                customer = UserAuth.objects.get(pk=pk)
                serializer = UserAuthSerializer(customer)
                return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
            except UserAuth.DoesNotExist:
                return Response({"status": "error", "message": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)

        customers = UserAuth.objects.all().order_by('-date_joined')
        serializer = UserAuthSerializer(customers, many=True)
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = UserAuthSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"status": "error", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk=None):
        try:
            customer = UserAuth.objects.get(pk=pk)
            serializer = UserAuthSerializer(customer, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
            return Response({"status": "error", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except UserAuth.DoesNotExist:
            return Response({"status": "error", "message": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk=None):
        try:
            customer = UserAuth.objects.get(pk=pk)
            customer.delete()
            return Response({"status": "success", "message": "Customer deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except UserAuth.DoesNotExist:
            return Response({"status": "error", "message": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_profile = request.user  # Access the current logged-in user
            serializer = UserAuthSerializer(user_profile)  # Serialize the user data
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UserAuth.DoesNotExist:
            return Response({'status': 'error',"message": "User profile not found."}, status=status.HTTP_404_NOT_FOUND)
        
    def patch(self, request):
        customer = request.user  # Access the current logged-in user
        serializer = UserAuthSerializer(customer, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"status": "error", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class AreaViewSet(viewsets.ModelViewSet):
    queryset = Area.objects.all()
    serializer_class = AreaSerializer

class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
