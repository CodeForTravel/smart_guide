from django.urls import re_path
from apps.chat.consumers import ChatConsumer

websocket_urlpatterns = [
    re_path(r"ws/chat/threads/(?P<thread_id>[^/]+)/$", ChatConsumer.as_asgi()),
]
