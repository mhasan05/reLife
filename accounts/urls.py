from django.urls import path
from .views import CustomerView,LoginView,UserProfileView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('user_profile/', UserProfileView.as_view(), name='user_profile'),
    path('user/', CustomerView.as_view(), name='user-list'),
    path('user/<int:pk>/', CustomerView.as_view(), name='user-detail'),
    
]

