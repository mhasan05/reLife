from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Product,Company,Category
from .serializers import ProductSerializer,CompanySerializer,CategorySerializer
from rest_framework.permissions import IsAuthenticated

class ProductView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            try:
                product = Product.objects.get(pk=pk)
                serializer = ProductSerializer(product)
                return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
            except Product.DoesNotExist:
                return Response({"status": "error", "message": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        products = Product.objects.filter(is_active=True).order_by('-created_on')
        total_products = Product.objects.filter(is_active=True).count()
        serializer = ProductSerializer(products, many=True)
        return Response({"status": "success", "total_products": total_products, "data": serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"status": "error", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk=None):
        try:
            product = Product.objects.get(pk=pk)
            serializer = ProductSerializer(product, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
            return Response({"status": "error", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Product.DoesNotExist:
            return Response({"status": "error", "message": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk=None):
        try:
            product = Product.objects.get(pk=pk)
            product.delete()
            return Response({"status": "success", "message": "Product deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Product.DoesNotExist:
            return Response({"status": "error", "message": "Product not found"}, status=status.HTTP_404_NOT_FOUND)


class CompanyView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            try:
                company = Company.objects.get(pk=pk)
                serializer = CompanySerializer(company)
                return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
            except Company.DoesNotExist:
                return Response({"status": "error", "message": "Company not found"}, status=status.HTTP_404_NOT_FOUND)

        companies = Company.objects.filter(is_active=True).order_by('-created_on')
        total_companies = Company.objects.filter(is_active=True).count()
        serializer = CompanySerializer(companies, many=True)
        return Response({"status": "success", "total_companies": total_companies, "data": serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CompanySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"status": "error", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk=None):
        try:
            company = Company.objects.get(pk=pk)
            serializer = CompanySerializer(company, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
            return Response({"status": "error", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Company.DoesNotExist:
            return Response({"status": "error", "message": "Company not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk=None):
        try:
            company = Company.objects.get(pk=pk)
            company.delete()
            return Response({"status": "success", "message": "Company deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Company.DoesNotExist:
            return Response({"status": "error", "message": "Company not found"}, status=status.HTTP_404_NOT_FOUND)
        


class CategoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            try:
                category = Category.objects.get(pk=pk)
                serializer = CategorySerializer(category)
                return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
            except Category.DoesNotExist:
                return Response({"status": "error", "message": "Category not found"}, status=status.HTTP_404_NOT_FOUND)

        categories = Category.objects.all().order_by('-created_on')
        total_categories = Category.objects.count()
        serializer = CategorySerializer(categories, many=True)
        return Response({"status": "success", "total_categories": total_categories, "data": serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"status": "error", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk=None):
        try:
            category = Category.objects.get(pk=pk)
            serializer = CategorySerializer(category, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
            return Response({"status": "error", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Category.DoesNotExist:
            return Response({"status": "error", "message": "Category not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk=None):
        try:
            category = Category.objects.get(pk=pk)
            category.delete()
            return Response({"status": "success", "message": "Category deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Category.DoesNotExist:
            return Response({"status": "error", "message": "Category not found"}, status=status.HTTP_404_NOT_FOUND)