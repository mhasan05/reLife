from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Product,Company,Category
from .serializers import ProductSerializer,CompanySerializer,CategorySerializer
from rest_framework.permissions import IsAuthenticated
from django.db.models import Prefetch
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination


class ProductPagination(PageNumberPagination):
    page_size = 10  # default page size
    page_size_query_param = 'page_size'  # let client override page size using ?page_size=
    max_page_size = 500



class ProductView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = ProductPagination()

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
        # Apply pagination
        paginator = self.pagination_class
        paginated_products = paginator.paginate_queryset(products, request)

        serializer = ProductSerializer(paginated_products, many=True)
        # Return paginated response
        return paginator.get_paginated_response({
            "status": "success",
            "total_products": total_products,
            "data": serializer.data
        })

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


class CategoryWiseProductView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        """
        Fetch products by category or group products by all categories.
        """
        try:
            if pk:
                # Fetch products for a specific category using `category_id`
                category = Category.objects.get(category_id=pk)  # Use category_id explicitly
                products = category.products.filter(is_active=True).order_by('-created_on')
                serializer = ProductSerializer(products, many=True)
                return Response({
                    "status": "success",
                    "category": {
                        "category_id": category.category_id,
                        "name": category.name
                    },
                    "data": serializer.data
                }, status=status.HTTP_200_OK)

            # Fetch products grouped by category
            categories = Category.objects.prefetch_related(
                Prefetch(
                    'products',
                    queryset=Product.objects.filter(is_active=True).order_by('-created_on'),
                    to_attr='active_products'
                )
            )

            result = []
            for category in categories:
                if hasattr(category, 'active_products') and category.active_products:
                    result.append({
                        "category_id": category.category_id,  # Use category_id explicitly
                        "category_name": category.name,
                        "products": ProductSerializer(category.active_products, many=True).data
                    })

            return Response({"status": "success", "data": result}, status=status.HTTP_200_OK)

        except Category.DoesNotExist:
            return Response({"status": "error", "message": "Category not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProductSearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Search for products by product name or company name.
        """
        query = request.query_params.get('q', '')  # Get the search query from request
        if not query:
            return Response(
                {"status": "error", "message": "Query parameter 'q' is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Search for products by product name or company name
            products = Product.objects.filter(
                Q(product_name__icontains=query) |  # Case-insensitive search for product name
                Q(company_id__company_name__icontains=query) |  # Case-insensitive search for company name
                Q(generic_name__icontains=query)  # Case-insensitive search for generic name
            ).filter(is_active=True).distinct()

            # Serialize the results
            serializer = ProductSerializer(products, many=True)
            return Response(
                {"status": "success", "query": query, "data": serializer.data},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CompanyProductSearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Search for products by multiple company names (partial match).
        """
        company_names_param = request.query_params.get('company_names', '')
        if not company_names_param:
            return Response(
                {"status": "error", "message": "Query parameter 'company_names' is required (comma-separated)."},
                status=status.HTTP_400_BAD_REQUEST
            )

        company_names = [name.strip() for name in company_names_param.split(',') if name.strip()]
        if not company_names:
            return Response(
                {"status": "error", "message": "No valid company names provided."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Partial match (case-insensitive) for multiple names
            from functools import reduce
            from operator import or_
            filters = reduce(or_, [Q(company_name__icontains=name) for name in company_names])
            companies = Company.objects.filter(filters)

            if not companies.exists():
                return Response(
                    {"status": "success", "message": "No companies found.", "data": []},
                    status=status.HTTP_200_OK
                )

            products = Product.objects.filter(
                company_id__in=companies,
                is_active=True
            ).distinct()

            serializer = ProductSerializer(products, many=True)
            return Response(
                {
                    "status": "success",
                    "selected_companies": company_names,
                    "total_products": products.count(),
                    "data": serializer.data
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


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