from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Product,Company,Category
from .serializers import ProductSerializer,CompanySerializer,CategorySerializer
from rest_framework.permissions import IsAuthenticated
from django.db.models import Prefetch
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination
from functools import reduce
from operator import or_


class ProductPagination(PageNumberPagination):
    page_size = 10  # default page size
    page_size_query_param = 'page_size'  # let client override page size using ?page_size=
    max_page_size = 500

class AllProductView(APIView):
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

        user = request.user
        if user.is_superuser:
            products = Product.objects.all().order_by('-created_on')
            total_products = Product.objects.all().count()
        else:
            products = Product.objects.filter(is_active=True).order_by('product_name')
            total_products = Product.objects.filter(is_active=True).count()
            
        
        # Apply pagination
        paginator = self.pagination_class
        paginated_products = paginator.paginate_queryset(products, request)

        serializer = ProductSerializer(products, many=True)
        # Return paginated response
        return paginator.get_paginated_response({
            "status": "success",
            "total_products": total_products,
            "data": serializer.data
        })

class ProductView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = ProductPagination()

    def get(self, request, pk=None):
        src = request.query_params.get('src')
        if src:
            # Filter product by name
            product = Product.objects.filter(product_name__istartswith=src)
            if not product:
                product = Product.objects.filter(product_name__icontains=src)
            # Apply pagination
            paginator = self.pagination_class
            paginated_product = paginator.paginate_queryset(product, request)
            serializer = ProductSerializer(paginated_product, many=True)
            return paginator.get_paginated_response({
                "status": "success",
                "data": serializer.data
            })
        if pk:
            try:
                product = Product.objects.get(pk=pk)
                serializer = ProductSerializer(product)
                return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
            except Product.DoesNotExist:
                return Response({"status": "error", "message": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        user = request.user
        if user.is_superuser:
            products = Product.objects.all().order_by('-created_on')
            total_products = Product.objects.all().count()
        else:
            products = Product.objects.filter(is_active=True).order_by('product_name')
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

class ProductNameListView(APIView):
    def get(self, request):
        # Get all product names as a list
        product_names = list(
            Product.objects.order_by("product_name").values_list("product_name", flat=True)
        )
        return Response({"status": "success", "data": product_names}, status=status.HTTP_200_OK)
    
class GenericNameListView(APIView):
    def get(self, request):
        # Get all product names as a list
        generic_names = list(
            GenericName.objects.order_by("name").values_list("name", flat=True)
        )
        return Response({"status": "success", "data": generic_names}, status=status.HTTP_200_OK)

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
                products = category.products.filter(is_active=True).order_by('product_name')
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
                    queryset=Product.objects.filter(is_active=True).order_by('product_name'),
                    to_attr='active_products'
                )
            )
            
            preferred_order = ["Tablet", "Capsule"]

            # First, categories that match preferred order
            ordered_categories = sorted(
                categories,
                key=lambda c: (preferred_order.index(c.name) if c.name in preferred_order else len(preferred_order), c.name)
            )

            result = []
            for category in ordered_categories:
                if hasattr(category, 'active_products') and category.active_products:
                    result.append({
                        "category_id": category.category_id,  # Use category_id explicitly
                        "category_name": category.name,
                        "products": ProductSerializer(category.active_products, many=True).data
                        # "products": ProductSerializer(category.active_products[:7], many=True).data
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
                Q(product_name__icontains=query)
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



class GenericNameProductSearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Search for products by multiple generic names (partial match).
        """
        generic_names_param = request.query_params.get('generic_names', '')
        if not generic_names_param:
            return Response(
                {"status": "error", "message": "Query parameter 'generic_names' is required (comma-separated)."},
                status=status.HTTP_400_BAD_REQUEST
            )

        generic_names = [name.strip() for name in generic_names_param.split(',') if name.strip()]
        if not generic_names:
            return Response(
                {"status": "error", "message": "No valid generic names provided."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Partial match (case-insensitive) for multiple generic names
            filters = reduce(or_, [Q(name__icontains=name) for name in generic_names])
            generics = GenericName.objects.filter(filters)

            if not generics.exists():
                return Response(
                    {"status": "success", "message": "No generic names found.", "data": []},
                    status=status.HTTP_200_OK
                )

            products = Product.objects.filter(
                generic_name__in=generics,
                is_active=True
            ).distinct()

            serializer = ProductSerializer(products, many=True)
            return Response(
                {
                    "status": "success",
                    "selected_generic_names": generic_names,
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

        companies = Company.objects.filter(is_active=True).order_by('company_name')
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
        
class GenericView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            try:
                generic_name = GenericName.objects.get(pk=pk)
                serializer = GenericNameSerializer(generic_name)
                return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
            except GenericName.DoesNotExist:
                return Response({"status": "error", "message": "Generic Name not found"}, status=status.HTTP_404_NOT_FOUND)

        generic_name = GenericName.objects.all().order_by('name')
        total_name = GenericName.objects.count()
        serializer = GenericNameSerializer(generic_name, many=True)
        return Response({"status": "success", "total_name": total_name, "data": serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = GenericNameSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"status": "error", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk=None):
        try:
            generic_name = GenericName.objects.get(pk=pk)
            serializer = GenericNameSerializer(generic_name, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)
            return Response({"status": "error", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except GenericName.DoesNotExist:
            return Response({"status": "error", "message": "Generic Name not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk=None):
        try:
            generic_name = GenericName.objects.get(pk=pk)
            generic_name.delete()
            return Response({"status": "success", "message": "Generic Name deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except GenericName.DoesNotExist:
            return Response({"status": "error", "message": "Generic Name not found"}, status=status.HTTP_404_NOT_FOUND)
        




from .models import BannerImages
from .serializers import *
from django.shortcuts import get_object_or_404

class BannerImagesListCreateView(APIView):
    def get(self, request):
        banners = BannerImages.objects.all().order_by('-created_on')
        serializer = BannerImageSerializer(banners, many=True)
        return Response({'status':'success','data':serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = BannerImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status':'success','data':serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BannerImagesDetailView(APIView):
    def get(self, request, pk):
        banner = get_object_or_404(BannerImages, pk=pk)
        serializer = BannerImageSerializer(banner)
        return Response({'status':'success','data':serializer.data},status=status.HTTP_200_OK)

    def patch(self, request, pk):
        banner = get_object_or_404(BannerImages, pk=pk)
        serializer = BannerImageSerializer(banner, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'status':'success','data':serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        banner = get_object_or_404(BannerImages, pk=pk)
        banner.delete()
        return Response({'status':'success','message':'successfully delete'},status=status.HTTP_200_OK)


class AddProductToBatch(APIView):
    def post(self, request):
        product_id = request.data.get("product_id")
        new_stock_quantity = request.data.get("new_stock_quantity", 0)
        new_cost_price = request.data.get("new_cost_price", 0)
        mrp = request.data.get("mrp", 0)
        new_selling_price = request.data.get("new_selling_price", 0)
        batch_id = request.data.get("batch_id")  # If frontend sends it
        user = request.user  # assuming request.user is from UserAuth

        # If no batch id sent, create a new one
        check_batch = TempProduct.objects.filter(is_confirmed=False, user_id=user).first()
        if check_batch:
            batch_id = check_batch.batch_id
        else:
            batch_id = uuid.uuid4()

        product = get_object_or_404(Product, pk=product_id)

        temp = TempProduct.objects.create(
            batch_id=batch_id,
            user_id=user,
            product_id=product,
            new_stock_quantity=new_stock_quantity,
            new_cost_price=new_cost_price,
            new_selling_price=new_selling_price,
            mrp=mrp,
        )

        return Response(
            {
                "message": "Product staged successfully",
                "batch_id": str(temp.batch_id),
                "temp_id": temp.id,
            },
            status=status.HTTP_201_CREATED,
        )
    





class BatchSummary(APIView):
    def get(self, request, batch_id):
        updates = TempProduct.objects.filter(batch_id=batch_id, user_id=request.user, is_confirmed=False)

        if not updates.exists():
            return Response({"message": "No products in this batch"}, status=status.HTTP_404_NOT_FOUND)

        total_value = sum([u.total_amount for u in updates])
        data = [
            {
                "id": u.id,
                "product": u.product_id.product_name,
                "stock": u.new_stock_quantity,
                "cost_price": str(u.new_cost_price),
                "mrp": str(u.mrp),
                "selling_price": str(u.new_selling_price),
                "total": str(u.total_amount),
            }
            for u in updates
        ]
        return Response(
            {
                "batch_id": batch_id,
                "products": data,
                "total_products": updates.count(),
                "total_value": str(total_value),
            }
        )



class GetBatchSummary(APIView):
    def get(self, request, batch_id):
        updates = TempProduct.objects.filter(batch_id=batch_id, user_id=request.user, is_confirmed=True)

        if not updates.exists():
            return Response({"message": "No products in this batch"}, status=status.HTTP_404_NOT_FOUND)

        total_value = sum([u.total_amount for u in updates])
        data = [
            {
                "id": u.id,
                "product": u.product_id.product_name,
                "stock": u.new_stock_quantity,
                "cost_price": str(u.new_cost_price),
                "mrp": str(u.mrp),
                "selling_price": str(u.new_selling_price),
                "total": str(u.total_amount),
            }
            for u in updates
        ]
        return Response(
            {
                "batch_id": batch_id,
                "products": data,
                "total_products": updates.count(),
                "total_value": str(total_value),
            }
        )



class ConfirmBatch(APIView):
    def post(self, request, batch_id):
        updates = TempProduct.objects.filter(batch_id=batch_id, user_id=request.user, is_confirmed=False)

        if not updates.exists():
            return Response({"message": "No pending updates for this batch"}, status=status.HTTP_404_NOT_FOUND)

        for update in updates:
            product = update.product_id
            product.stock_quantity += update.new_stock_quantity
            product.cost_price = update.new_cost_price
            product.selling_price = update.new_selling_price
            product.save()

            update.is_confirmed = True
            update.save()

        return Response({"message": f"Batch {batch_id} applied successfully"})



class CancelBatch(APIView):
    def post(self, request, batch_id):
        deleted_count, _ = TempProduct.objects.filter(batch_id=batch_id, user_id=request.user, is_confirmed=False).delete()
        return Response({"message": f"Batch {batch_id} cancelled. {deleted_count} items removed."})





class UniqueBatchListAPIView(APIView):
    def get(self, request):
        # Get only distinct batch_id values
        unique_batches = (
            TempProduct.objects.values_list("batch_id", flat=True)
            .distinct()
        )

        # Remove duplicates and keep them as list of dicts
        unique_batches = [{"batch_id": bid} for bid in set(unique_batches)]

        return Response(
            {"status": "success", "data": unique_batches},
            status=status.HTTP_200_OK,
        )
