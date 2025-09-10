# urls.py
from django.urls import path
from .views import SiteInfoListCreateAPIView

urlpatterns = [
    path('site_info/', SiteInfoListCreateAPIView.as_view(), name='site_info_list_create'),
]
