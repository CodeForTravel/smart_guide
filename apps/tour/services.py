from django.db import transaction

from apps.tour.models import TourPlan, TourPlanPOI
from rest_framework.exceptions import ValidationError
from apps.tour.models import TourSession, NarrationMemory, PathPoint, POI
from apps.chat.models import ChatThread
from apps.users.services import UserPreferencesService
from apps.tour.utils import haversine_distance


class TourPlanService:
    @transaction.atomic
    def create(self, validated_data: dict) -> TourPlan:
        """
        Creates a TourPlan along with its ordered list of POIs.

        Args:
            validated_data: Deserialized and validated data from TourPlanSerializer.
                            May include 'pois_data': list of {'poi': POI, 'order': int}.

        Returns:
            The newly created TourPlan instance.
        """
        pois_data = validated_data.pop("pois_data", [])
        tour_plan = TourPlan.objects.create(**validated_data)
        self._create_plan_pois(tour_plan, pois_data)
        return tour_plan

    @transaction.atomic
    def update(self, instance: TourPlan, validated_data: dict) -> TourPlan:
        """
        Updates a TourPlan and replaces its POI list if pois_data is provided.

        If 'pois_data' is omitted from the request, the existing POIs are left untouched.
        If 'pois_data' is provided (even as an empty list), the existing POIs are replaced.

        Args:
            instance: The existing TourPlan instance to update.
            validated_data: Deserialized and validated data from TourPlanSerializer.

        Returns:
            The updated TourPlan instance.
        """
        pois_data = validated_data.pop("pois_data", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if pois_data is not None:
            instance.plan_pois.all().delete()
            self._create_plan_pois(instance, pois_data)

        return instance

    def _create_plan_pois(self, tour_plan: TourPlan, pois_data: list) -> None:
        """Internal helper to bulk-create TourPlanPOI entries."""
        TourPlanPOI.objects.bulk_create(
            [TourPlanPOI(tour_plan=tour_plan, poi=item["poi"], order=item["order"]) for item in pois_data]
        )


class TourSessionService:
    @transaction.atomic
    def create(self, user, validated_data: dict):
        """
        Creates a TourSession for the given user.

        Rules:
        - Only one active session (end_time=None) is allowed per user at a time.
          If one exists, raises ValidationError (HTTP 409).
        - Automatically creates a linked ChatThread for the session.

        Returns:
            The newly created TourSession instance (with .chat_thread pre-fetched).
        """

        active = TourSession.objects.filter(user=user, end_time__isnull=True).first()
        if active:
            raise ValidationError(
                {
                    "detail": f"You already have an active tour session (id={active.id}). End it before starting a new one."
                },
                code="conflict",
            )

        session = TourSession.objects.create(user=user, **validated_data)
        ChatThread.objects.create(user=user, tour_session=session)
        return session

    def get_active_session_for_user(self, session_id, user):
        """
        Retrieves an active TourSession by ID that belongs to the user.
        Pre-fetches city and chat_thread to support downstream POI/Chat logic.
        """
        try:
            return TourSession.objects.select_related("city", "chat_thread").get(id=session_id, user=user)
        except TourSession.DoesNotExist:
            return None

    def save_path_point(self, session, latitude, longitude, timestamp):
        """Records a user's geographical coordinate at a specific time."""
        return PathPoint.objects.create(session=session, latitude=latitude, longitude=longitude, timestamp=timestamp)


class POIService:
    def process_location_for_pois(self, session, user, latitude, longitude):
        """
        Main business logic for evaluating a user's new location against available POIs.
        1. Checks for POIs within the geofencing radius that haven't been narrated.
        2. Uses UserPreferences to match the best POI (stubbed).
        3. If no POIs are nearby, fetches mock POIs from a map API (stubbed).
        4. Generates an AI narration (stubbed) based on user's interests.
        5. Records the POI to memory to avoid repeating.

        Returns:
            list[dict]: A list of generated AI narrations with associated POI data.
        """
        triggered_pois = self._get_triggered_pois(session, latitude, longitude)
        prefs_service = UserPreferencesService()
        prefs = prefs_service.get_preferences(user)

        selected_pois = []
        if triggered_pois:
            # a) If multiples POIs, match with user preference. (Stub logic for demo)
            if len(triggered_pois) > 1 and prefs:
                # Stub: just pick the first one to simulate 'best match'
                selected_pois = [triggered_pois[0][0]]
            else:
                selected_pois = [poi for poi, _ in triggered_pois]
        else:
            # b) If no POIs in database, look into map in certain radius and extract 4-5 POI
            # Send it to AI along with user interest profile data
            mock_pois = self._fetch_pois_from_map(latitude, longitude)
            selected_pois = mock_pois

        narrations = []
        # c) Always generate narration for user based on preferences
        if selected_pois:
            for poi in selected_pois:
                self._record_narration_memory(session, poi, latitude, longitude)

                pref_score = prefs.interest_history_score if prefs else 5
                # TODO: STUB: sent to AI along with user interest profile data, context, and POIs
                ai_generated_narration = (
                    getattr(poi, "description_medium", None)
                    or f"Narration stub based on context. History score: {pref_score}"
                )

                narrations.append(
                    {
                        "poi_id": getattr(poi, "id", None),
                        "poi_name": poi.name,
                        "narration": ai_generated_narration,
                        "distance_meters": 0.0,
                    }
                )

        return narrations

    def _get_triggered_pois(self, session, latitude, longitude):
        """
        Returns a list of POIs within their geofencing radius that haven't been
        narrated yet in this session.
        """
        already_narrated = NarrationMemory.objects.filter(session=session).values_list("poi_id", flat=True)
        city_pois = POI.objects.filter(city=session.city, is_active=True).exclude(id__in=already_narrated)

        triggered = []
        for poi in city_pois:
            distance = haversine_distance(latitude, longitude, poi.latitude, poi.longitude)
            if distance <= poi.radius_meters:
                triggered.append((poi, round(distance, 1)))
        return triggered

    def _record_narration_memory(self, session, poi, latitude, longitude):
        """Saves memory that a POI was narrated during this session."""
        if getattr(poi, "id", None):  # ensure it's not a mock POI without an ID
            NarrationMemory.objects.create(session=session, poi=poi, latitude=latitude, longitude=longitude)

    def _fetch_pois_from_map(self, latitude, longitude):
        """Stub function to simulate fetching POIs from a map API if DB has none."""
        return [
            type("MockPOI", (object,), {"name": f"Map POI {i}", "description_medium": f"A generated map POI {i}."})()
            for i in range(1, 5)
        ]
