from django.urls import path, include

app_name = "chat"

urlpatterns = [
    path("api/v1/chat/", include("apps.chat.api.v1.urls", namespace="v1")),
]
