from django.db import models
from django.utils import timezone
from common.base_model import BaseModel
from django.contrib.auth import get_user_model

User = get_user_model()


class City(BaseModel):
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name}, {self.country}"


class POI(BaseModel):
    class POICategory(models.TextChoices):
        LANDMARK = "landmark", "Landmark"
        MUSEUM = "museum", "Museum"
        FOOD = "food", "Food"
        ARCHITECTURE = "architecture", "Architecture"
        NATURE = "nature", "Nature"
        CULTURE = "culture", "Culture"

    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="pois")
    category = models.CharField(max_length=100, blank=True, null=True, choices=POICategory.choices)
    name = models.CharField(max_length=200)

    # Optional curated narration
    description_short = models.TextField(blank=True, null=True)
    description_medium = models.TextField(blank=True, null=True)
    description_deep = models.TextField(blank=True, null=True)

    latitude = models.FloatField()
    longitude = models.FloatField()
    radius_meters = models.PositiveIntegerField(default=50)  # geofencing radius

    # If False, this is a dynamic/random spot discovered during a walk
    curated = models.BooleanField(default=True)
    priority_score = models.FloatField(default=0)  # 1-10 for triggering precedence
    tags = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.city.name})"


class TourPlan(BaseModel):
    """
    Pre-defined curated routes that any user can select.
    """

    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="tour_plans")
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    estimated_duration_minutes = models.PositiveIntegerField(default=60)

    def __str__(self):
        return f"{self.name} - {self.city.name}"


class TourPlanPOI(BaseModel):
    """
    The ordered list of POIs that make up a pre-defined TourPlan.
    Used by the mobile app to draw the suggested path on a map.
    """

    tour_plan = models.ForeignKey(TourPlan, on_delete=models.CASCADE, related_name="plan_pois")
    poi = models.ForeignKey(POI, on_delete=models.CASCADE)
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.tour_plan.name} -> {self.poi.name} (Stop {self.order})"


class TourSession(BaseModel):
    """
    Tracks a user's actual walk/session in real-time.
    """

    class SessionType(models.TextChoices):
        CURATED = "curated", "Curated"
        CUSTOM = "custom", "Custom"
        RANDOM = "random", "Random"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sessions")
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    tour_plan = models.ForeignKey(TourPlan, on_delete=models.SET_NULL, null=True, blank=True)
    session_type = models.CharField(max_length=20, choices=SessionType.choices, default=SessionType.CURATED)

    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Session {self.id} - {self.user.email} in {self.city.name}"


class PathPoint(BaseModel):
    """
    Logged every X seconds during a TourSession to draw the actual
    path the user walked historically.
    """

    session = models.ForeignKey(TourSession, on_delete=models.CASCADE, related_name="path_points")
    latitude = models.FloatField()
    longitude = models.FloatField()
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["timestamp"]

    def __str__(self):
        return f"Point at {self.timestamp} for Session {self.session.id}"


class NarrationMemory(BaseModel):
    """
    Tracks which POIs (curated or dynamic) the AI has already spoken about
    so it doesn't repeat itself. Also provides a history of places visited.
    """

    session = models.ForeignKey(TourSession, on_delete=models.CASCADE, related_name="narration_memory")
    poi = models.ForeignKey(POI, on_delete=models.CASCADE)
    latitude = models.FloatField(help_text="Exact lat when triggered")
    longitude = models.FloatField(help_text="Exact lon when triggered")
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["timestamp"]

    def __str__(self):
        return f"Narrated {self.poi.name} at {self.timestamp}"
