from django.urls import re_path
from apps.tour.consumers import LocationConsumer

websocket_urlpatterns = [
    re_path(r"ws/tour/sessions/(?P<session_id>[^/]+)/location/$", LocationConsumer.as_asgi()),
]
