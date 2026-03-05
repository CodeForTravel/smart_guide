from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.chat.api.v1.views import ChatThreadViewSet

app_name = "chat"

router = DefaultRouter()
router.register(r"threads", ChatThreadViewSet, basename="thread")

urlpatterns = [
    path("", include(router.urls)),
]
