from rest_framework import serializers
from apps.tour.models import City, POI, TourPlan, TourPlanPOI, TourSession


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ["id", "name", "country", "description", "created_at", "updated_at", "is_active"]
        read_only_fields = ["id", "created_at", "updated_at"]


class POISerializer(serializers.ModelSerializer):
    class Meta:
        model = POI
        fields = [
            "id",
            "city",
            "category",
            "name",
            "description_short",
            "description_medium",
            "description_deep",
            "latitude",
            "longitude",
            "radius_meters",
            "curated",
            "priority_score",
            "tags",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class TourPlanPOISerializer(serializers.ModelSerializer):
    poi = POISerializer(read_only=True)

    class Meta:
        model = TourPlanPOI
        fields = ["id", "poi", "order"]


class TourPlanSerializer(serializers.ModelSerializer):
    # Nested representation to show the exact list of POIs in order
    plan_pois = TourPlanPOISerializer(many=True, read_only=True)
    city_name = serializers.CharField(source="city.name", read_only=True)

    class Meta:
        model = TourPlan
        fields = [
            "id",
            "city",
            "city_name",
            "name",
            "description",
            "estimated_duration_minutes",
            "plan_pois",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class TourSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TourSession
        fields = [
            "id",
            "user",
            "city",
            "tour_plan",
            "session_type",
            "start_time",
            "end_time",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "start_time", "created_at", "updated_at"]
