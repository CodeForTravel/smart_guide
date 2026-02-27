from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.tour.api.v1.views import CityViewSet, TourPlanViewSet, POIViewSet, TourSessionViewSet

app_name = "tour"

router = DefaultRouter()
router.register(r"cities", CityViewSet, basename="city")
router.register(r"plans", TourPlanViewSet, basename="tourplan")
router.register(r"pois", POIViewSet, basename="poi")
router.register(r"tour-sessions", TourSessionViewSet, basename="tour_session")

urlpatterns = [
    path("", include(router.urls)),
]
