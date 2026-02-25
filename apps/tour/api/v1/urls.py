from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.tour.api.v1.views import CityViewSet, TourPlanViewSet, POIViewSet

app_name = "tour"

router = DefaultRouter()
router.register(r"cities", CityViewSet, basename="city")
router.register(r"plans", TourPlanViewSet, basename="tourplan")
router.register(r"pois", POIViewSet, basename="poi")

urlpatterns = [
    path("", include(router.urls)),
]
