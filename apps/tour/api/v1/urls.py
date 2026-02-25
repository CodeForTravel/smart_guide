from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.tour.api.v1.views import CityViewSet

app_name = "tour"

router = DefaultRouter()
router.register(r"cities", CityViewSet, basename="city")

urlpatterns = [
    path("", include(router.urls)),
]
