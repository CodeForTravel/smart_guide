from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from apps.tour.models import City, TourPlan, POI
from apps.tour.api.v1.serializers import CitySerializer, TourPlanSerializer, POISerializer
from apps.tour.filters import TourPlanFilter, POIFilter


class CityViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows cities to be viewed.
    For MVP, assuming cities are managed via Django Admin, so making it ReadOnly.
    """

    queryset = City.objects.filter(is_active=True).order_by("name")
    serializer_class = CitySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class TourPlanViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing pre-defined Curated Routes.
    Returns the TourPlan along with its ordered list of POIs.
    """

    queryset = TourPlan.objects.prefetch_related("plan_pois__poi", "city").filter(is_active=True)
    serializer_class = TourPlanSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = TourPlanFilter


class POIViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing Points of Interest.
    """

    queryset = POI.objects.select_related("city").filter(is_active=True)
    serializer_class = POISerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = POIFilter
