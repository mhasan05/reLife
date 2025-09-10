from django.urls import path
from .views import NoticeListCreateAPIView, NoticeDetailAPIView

urlpatterns = [
    path('notices/', NoticeListCreateAPIView.as_view(), name='notice_list_create'),
    path('notices/<int:pk>/', NoticeDetailAPIView.as_view(), name='notice_detail'),
]
