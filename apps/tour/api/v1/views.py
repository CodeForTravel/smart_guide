from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from apps.tour.models import City, TourPlan, POI
from apps.tour.api.v1.serializers import CitySerializer, TourPlanSerializer, POISerializer


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

    def get_queryset(self):
        """Allow filtering tour plans by city_id"""
        queryset = super().get_queryset()
        city_id = self.request.query_params.get("city_id")
        if city_id:
            queryset = queryset.filter(city_id=city_id)
        return queryset


class POIViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing Points of Interest.
    """

    queryset = POI.objects.select_related("city").filter(is_active=True)
    serializer_class = POISerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """Allow filtering POIs by city_id and curated status"""
        queryset = super().get_queryset()
        city_id = self.request.query_params.get("city_id")
        curated = self.request.query_params.get("curated")

        if city_id:
            queryset = queryset.filter(city_id=city_id)
        if curated is not None:
            # Convert string 'true'/'false' to boolean
            is_curated = str(curated).lower() in ["true", "1", "t"]
            queryset = queryset.filter(curated=is_curated)

        return queryset
