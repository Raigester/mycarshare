from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Authentication
    path('login/', views.CustomLoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='logout.html'), name='logout'),
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    
    # User profile
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('change-password/', views.change_password_view, name='change-password'),
    
    # Driver verification
    path('verification/new/', views.DriverLicenseVerificationCreateView.as_view(), name='verification-create'),
    path('verification/list/', views.DriverLicenseVerificationListView.as_view(), name='verification-list'),
    
    # Admin verification pages
    path('admin/verifications/', views.AdminVerificationListView.as_view(), name='admin-verification-list'),
    path('admin/verification/<int:pk>/', views.AdminVerificationUpdateView.as_view(), name='admin-verification-detail'),
    
    # Balance management
    path('balance/', views.user_balance_view, name='balance'),
]