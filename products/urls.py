from django.urls import path
from .views import *

urlpatterns = [
    path('products/', ProductView.as_view(), name='product_list'),
    path('products/<int:pk>/', ProductView.as_view(), name='product_detail'),

    path('product_names/', ProductNameListView.as_view(), name='product_names'),


    path('products/category/', CategoryWiseProductView.as_view(), name='product_detail_category'),
    path('products/category/<int:pk>/', CategoryWiseProductView.as_view(), name='product_detail_category'),

    path('products/search/', ProductSearchView.as_view(), name='product_search'),
    path('search/by_companies/', CompanyProductSearchView.as_view(), name='company_product_search'),

    path('companies/', CompanyView.as_view(), name='company_list'),
    path('companies/<int:pk>/', CompanyView.as_view(), name='company_detail'),

    path('categories/', CategoryView.as_view(), name='category_list'),
    path('categories/<int:pk>/', CategoryView.as_view(), name='category_detail'),


    path('generic_name/', GenericView.as_view(), name='generic_name'),
    path('generic_name/<int:pk>/', GenericView.as_view(), name='generic_name_details'),

    path('generic_names/', GenericNameListView.as_view(), name='generic_names'),


    path('banners/', BannerImagesListCreateView.as_view(), name='banner-list-create'),
    path('banners/<int:pk>/', BannerImagesDetailView.as_view(), name='banner-detail'),
]

