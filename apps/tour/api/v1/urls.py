from django.urls import path
from rest_framework.routers import DefaultRouter

app_name = "tour"

router = DefaultRouter()
# router.register(r"tours", TourViewSet, basename="tours")

urlpatterns = [
    # path("some-view/", SomeView.as_view(), name="some-view"),
] + router.urls
