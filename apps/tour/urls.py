from django.urls import path, include

app_name = "tour"

urlpatterns = [
    path("api/v1/tour/", include("apps.tour.api.v1.urls", namespace="v1")),
]
