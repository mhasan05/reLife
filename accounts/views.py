from rest_framework import viewsets
from .models import UserAuth, Area, Address
from .serializers import UserAuthSerializer, AreaSerializer, AddressSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from accounts.models import Area
from rest_framework.pagination import PageNumberPagination


class UserPagination(PageNumberPagination):
    page_size = 10  # default page size
    page_size_query_param = 'page_size'  # let client override page size using ?page_size=
    max_page_size = 1000

class HomeView(APIView):
    def get(self,request):
        return Response({'status': 'success',"message": "Welcome to teamerror :)."})


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
        
        elif user.is_approved == False:
            return Response({'status': 'error', "message": "Wait for admin approval."}, status=status.HTTP_401_UNAUTHORIZED)


        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        return Response({
            'status': 'success',
            'access_token': str(access_token),
            'data': UserAuthSerializer(user).data
        }, status=status.HTTP_200_OK)


class AdminLoginView(APIView):
    """
    Handle user login.
    """
    def post(self, request):
        phone = request.data.get('phone')
        password = request.data.get('password')

        if not phone or not password:
            return Response({'status': 'error',"message": "Both phone and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, phone=phone, password=password)

        if user.is_superuser is False:
            return Response({'status': 'error', "message": "You are not authorized to access this resource."}, status=status.HTTP_403_FORBIDDEN)

        if user is None:
            return Response({'status': 'error', "message": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_active:
            return Response({'status': 'error', "message": "Your account is inactive."}, status=status.HTTP_400_BAD_REQUEST)

        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        return Response({
            'status': 'success',
            'access_token': str(access_token),
            'data': UserAuthSerializer(user).data
        }, status=status.HTTP_200_OK)


class SignupView(APIView):
    """
    Handle user signup.
    """
    def post(self, request):
        full_name = request.data.get('full_name')
        email = request.data.get('email')
        phone = request.data.get('phone')
        shop_name = request.data.get('shop_name')
        shop_address = request.data.get('shop_address')
        area_id = request.data.get('area_id')
        password = request.data.get('password')
        confirm_password = request.data.get('confirm_password')

        if not email or not phone or not shop_name or not shop_address or not area_id or not password or not full_name:
            return Response({'status':'error',"message": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

        elif UserAuth.objects.filter(email=email).exists():
            return Response({'status':'error',"message": "The email is already taken."}, status=status.HTTP_400_BAD_REQUEST)
        elif UserAuth.objects.filter(phone=phone).exists():
            return Response({'status':'error',"message": "The phone number is already taken."}, status=status.HTTP_400_BAD_REQUEST)

        elif password != confirm_password:
            return Response({'status':'error',"message": "Passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            pass
        area = Area.objects.filter(area_id=area_id).first()
        
        user = UserAuth(email=email, full_name=full_name, phone=phone, shop_name=shop_name, shop_address=shop_address, area=area)
        try:
            user.set_password(password)
            user.save()
        except:
            return Response({'status':'error',"message": "Failed to create user. Please try again."}, status=status.HTTP_400_BAD_REQUEST)

        # access_token, error = self.send_otp_and_respond(user)
        
        # if error:
        #     return Response({'status':'error',"message": error}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            'status': 'success',
            'message': 'User created successfully. Please log in.',
        }, status=status.HTTP_201_CREATED)


class CustomerView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = UserPagination()

    def get(self, request, pk=None):
        if pk:
            try:
                customer = UserAuth.objects.get(pk=pk)
                serializer = UserAuthSerializer(customer)
                return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
            except UserAuth.DoesNotExist:
                return Response({"status": "error", "message": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)
            
        
        
        customers = UserAuth.objects.all().order_by('-date_joined')
        paginator = self.pagination_class
        paginated_customers = paginator.paginate_queryset(customers, request)
        serializer = UserAuthSerializer(paginated_customers, many=True)
        return paginator.get_paginated_response({
            "status": "success",
            "data": serializer.data
        })

    def patch(self, request, pk=None):
        try:
            customer = UserAuth.objects.get(pk=pk)
            serializer = UserAuthSerializer(customer, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"status": "success", "message": "Customer approved successfully"}, status=status.HTTP_200_OK)
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

    def get(self, request, pk=None):
        try:
            user_profile = request.user  # Access the current logged-in user
            serializer = UserAuthSerializer(user_profile)  # Serialize the user data
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UserAuth.DoesNotExist:
            return Response({'status': 'error',"message": "User profile not found."}, status=status.HTTP_404_NOT_FOUND)
        
    def post(self, request, pk=None):
        user = request.user  # Access the current logged-in user
        if user.is_superuser:
            try:
                customer = UserAuth.objects.get(pk=pk)
                customer.is_approved = True  # Approve the customer
                customer.save()
                serializer = UserAuthSerializer(customer)
                return Response({"status": "success","message": "Customer approved successfully","data": serializer.data}, status=status.HTTP_200_OK)
            except UserAuth.DoesNotExist:
                return Response({"status": "error", "message": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"status": "error", "message": "You are not authorized to approve users."}, status=status.HTTP_403_FORBIDDEN)

    def patch(self, request, pk=None):
        customer = request.user  # Access the current logged-in user
        data = request.data.copy()
        # Only allow admin to change restricted fields
        restricted_fields = ['is_superuser','is_staff', 'is_active', 'is_approved']
        if not customer.is_superuser:
            for field in restricted_fields:
                data.pop(field, None)
        serializer = UserAuthSerializer(customer, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"status": "error", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class AreaViewSet(APIView):
    queryset = Area.objects.all()
    serializer_class = AreaSerializer
    def get(self, request, pk=None):
        if pk:
            try:
                area = Area.objects.get(pk=pk)
                serializer = AreaSerializer(area)
                return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
            except Area.DoesNotExist:
                return Response({"status": "error", "message": "Area not found"}, status=status.HTTP_404_NOT_FOUND)

        areas = Area.objects.all().order_by('-created_on')
        serializer = AreaSerializer(areas, many=True)
        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
    def post(self, request):
        serializer = AreaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"status": "error", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    def patch(self, request, pk=None):
        try:
            area = Area.objects.get(pk=pk)
            serializer = AreaSerializer(area, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
            return Response({"status": "error", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Area.DoesNotExist:
            return Response({"status": "error", "message": "Area not found"}, status=status.HTTP_404_NOT_FOUND)
    def delete(self, request, pk=None):
        try:
            area = Area.objects.get(pk=pk)
            area.delete()
            return Response({"status": "success", "message": "Area deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Area.DoesNotExist:
            return Response({"status": "error", "message": "Area not found"}, status=status.HTTP_404_NOT_FOUND)


class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
