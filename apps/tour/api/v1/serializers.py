from rest_framework import serializers
from apps.tour.models import City


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ["id", "name", "country", "description", "created_at", "updated_at", "is_active"]
        read_only_fields = ["id", "created_at", "updated_at"]
