import django_filters
from apps.tour.models import TourPlan, POI


class TourPlanFilter(django_filters.FilterSet):
    city_id = django_filters.NumberFilter(field_name="city_id")

    class Meta:
        model = TourPlan
        fields = ["city_id"]


class POIFilter(django_filters.FilterSet):
    city_id = django_filters.NumberFilter(field_name="city_id")
    curated = django_filters.BooleanFilter(field_name="curated")
    category = django_filters.CharFilter(field_name="category", lookup_expr="iexact")

    class Meta:
        model = POI
        fields = ["city_id", "curated", "category"]
