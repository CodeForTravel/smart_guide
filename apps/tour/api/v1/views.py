from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAuthenticatedOrReadOnly, SAFE_METHODS
from django_filters.rest_framework import DjangoFilterBackend
from apps.tour.models import City, TourPlan, POI, TourSession
from apps.tour.api.v1.serializers import CitySerializer, TourPlanSerializer, POISerializer, TourSessionSerializer
from apps.tour.filters import TourPlanFilter, POIFilter
from apps.tour.services import create_tour_plan, update_tour_plan
from common.permissions import IsSystemAdmin


class CityViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows cities to be viewed.
    For MVP, assuming cities are managed via Django Admin, so making it ReadOnly.
    """

    queryset = City.objects.filter(is_active=True).order_by("name")
    serializer_class = CitySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class POIViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing Points of Interest.
    """

    queryset = POI.objects.select_related("city").filter(is_active=True)
    serializer_class = POISerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = POIFilter


class TourPlanViewSet(viewsets.ModelViewSet):
    """
    API endpoint for viewing and managing pre-defined Curated Routes.
    - Read (list/retrieve): open to any authenticated or anonymous user.
    - Write (create/update/delete): restricted to admin/staff users only.
    Business logic is delegated to apps.tour.services.
    """

    queryset = TourPlan.objects.prefetch_related("plan_pois__poi", "city").filter(is_active=True)
    serializer_class = TourPlanSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = TourPlanFilter

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsAuthenticatedOrReadOnly()]
        return [permissions.IsAuthenticated(), IsSystemAdmin()]

    def perform_create(self, serializer):
        tour_plan = create_tour_plan(serializer.validated_data)
        # Re-assign instance so the response is serialized correctly
        serializer.instance = tour_plan

    def perform_update(self, serializer):
        updated_instance = update_tour_plan(serializer.instance, serializer.validated_data)
        # Keep serializer.instance in sync so the response reflects the updated data
        serializer.instance = updated_instance


class TourSessionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for viewing and creating TourSessions.
    Users can only view and manage their own sessions.
    """

    serializer_class = TourSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Prevent swagger generation from throwing an exception with AnonymousUser
        if getattr(self, "swagger_fake_view", False):
            return TourSession.objects.none()
        return TourSession.objects.filter(user=self.request.user).order_by("-start_time")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
