from django.urls import path
from .views import *

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('login/', LoginView.as_view(), name='login'),
    path('signup/', SignupView.as_view(), name='signup'),
    path('admin_login/', AdminLoginView.as_view(), name='admin_login'),

    path('user_profile/', UserProfileView.as_view(), name='user_profile'),
    path('user_approved/<int:pk>/', UserProfileView.as_view(), name='user_approved'),
    path('user/', CustomerView.as_view(), name='user_list'),
    path('user/<int:pk>/', CustomerView.as_view(), name='user_detail'),

    path('districts/', DistrictListAPIView.as_view(), name='district-list'),

    path('area/', AreaViewSet.as_view(), name='area_list'),
    path('area/<int:pk>/', AreaViewSet.as_view(), name='area_detail'),

]

