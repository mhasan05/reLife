from django.urls import path
from .views import ProductView,CompanyView,CategoryView

urlpatterns = [
    path('products/', ProductView.as_view(), name='product_list'),
    path('products/<int:pk>/', ProductView.as_view(), name='product_detail'),

    path('companies/', CompanyView.as_view(), name='company_list'),
    path('companies/<int:pk>/', CompanyView.as_view(), name='company_detail'),

    path('categories/', CategoryView.as_view(), name='category_list'),
    path('categories/<int:pk>/', CategoryView.as_view(), name='category_detail'),
]

