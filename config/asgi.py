"""
ASGI config for smart_guide_be project.
Handles both HTTP (Django) and WebSocket (Django Channels) connections.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Initialize Django ASGI app early to ensure apps are loaded before importing consumers
django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter  # noqa: E402
from common.middleware import JWTAuthMiddleware  # noqa: E402
from apps.tour.routing import websocket_urlpatterns as tour_ws_patterns  # noqa: E402
from apps.chat.routing import websocket_urlpatterns as chat_ws_patterns  # noqa: E402

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": JWTAuthMiddleware(URLRouter(tour_ws_patterns + chat_ws_patterns)),
    }
)
