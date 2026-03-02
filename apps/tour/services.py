from django.db import transaction

from apps.tour.models import TourPlan, TourPlanPOI


@transaction.atomic
def create_tour_plan(validated_data: dict) -> TourPlan:
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
    _create_tour_plan_pois(tour_plan, pois_data)
    return tour_plan


@transaction.atomic
def update_tour_plan(instance: TourPlan, validated_data: dict) -> TourPlan:
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
        _create_tour_plan_pois(instance, pois_data)

    return instance


def _create_tour_plan_pois(tour_plan: TourPlan, pois_data: list) -> None:
    """Internal helper to bulk-create TourPlanPOI entries."""
    TourPlanPOI.objects.bulk_create(
        [TourPlanPOI(tour_plan=tour_plan, poi=item["poi"], order=item["order"]) for item in pois_data]
    )
