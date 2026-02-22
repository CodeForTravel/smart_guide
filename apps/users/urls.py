from django.urls import path, include

app_name = "users"

urlpatterns = [
    path("api/v1/auth/", include("apps.users.api.v1.urls", namespace="v1")),
]
