from django.urls import path, re_path
from rest_framework_simplejwt.views import TokenRefreshView
from apps.users.api.v1.views import (
    RegisterView,
    LoginView,
    LogoutView,
    ChangePasswordView,
    PasswordResetView,
    PasswordResetConfirmView,
    AdminUserViewSet,
    GoogleLogin,
)
from rest_framework import routers


app_name = "users"

router = routers.SimpleRouter()
router.register("users", AdminUserViewSet, basename="users")


urlpatterns = [
    path("signup/", RegisterView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("change-password/", ChangePasswordView.as_view(), name="change_password"),
    path("password-reset/", PasswordResetView.as_view(), name="password_reset"),
    path("password-reset-confirm/", PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("google/", GoogleLogin.as_view(), name="google_login"),
] + router.urls
