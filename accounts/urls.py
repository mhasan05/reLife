from django.urls import path
from .views import CustomerView,LoginView,UserProfileView,AdminLoginView,SignupView,AreaViewSet

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('signup/', SignupView.as_view(), name='signup'),
    path('admin_login/', AdminLoginView.as_view(), name='admin_login'),

    path('user_profile/', UserProfileView.as_view(), name='user_profile'),
    path('user/', CustomerView.as_view(), name='user_list'),
    path('user/<int:pk>/', CustomerView.as_view(), name='user_detail'),

    path('area/', AreaViewSet.as_view(), name='area_list'),
    path('area/<int:pk>/', AreaViewSet.as_view(), name='area_detail'),

]

