from django.contrib.auth import views as auth_views
from django.urls import path

from . import views


urlpatterns = [
    # Аутентифікація
    path("login/", views.CustomLoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(template_name="logout.html"), name="logout"),
    path("register/", views.UserRegistrationView.as_view(), name="register"),

    # Верифікація електронної пошти
    path("verify-email/<uuid:token>/", views.EmailVerificationView.as_view(), name="verify-email"),
    path("resend-verification/", views.resend_verification_email, name="resend-verification"),

    # Профіль користувача
    path("profile/", views.UserProfileView.as_view(), name="profile"),
    path("change-password/", views.change_password_view, name="change-password"),

    # Верифікація водія
    path("verification/new/", views.DriverLicenseVerificationCreateView.as_view(), name="verification-create"),
    path("verification/list/", views.DriverLicenseVerificationListView.as_view(), name="verification-list"),

    # Сторінки верифікації для адміністратора
    path("admin/verifications/", views.AdminVerificationListView.as_view(), name="admin-verification-list"),
    path("admin/verification/<int:pk>/", views.AdminVerificationUpdateView.as_view(), name="admin-verification-detail"),

    # Управління балансом
    path("balance/", views.user_balance_view, name="balance"),
]
