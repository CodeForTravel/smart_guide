import urllib.parse

from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()


@database_sync_to_async
def get_user_from_token(token_key: str):
    """
    Validates a JWT access token from the WebSocket query string and returns
    the corresponding user. Returns AnonymousUser if the token is invalid.
    """
    try:
        token = AccessToken(token_key)
        return User.objects.get(id=token["user_id"])
    except Exception:
        return AnonymousUser()


class JWTAuthMiddleware:
    """
    ASGI middleware that reads a JWT token from the WebSocket query string
    (?token=<access_token>) and attaches the authenticated user to scope["user"].

    Usage in asgi.py:
        JWTAuthMiddleware(URLRouter(...))
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        query_string = scope.get("query_string", b"").decode()
        params = urllib.parse.parse_qs(query_string)
        token_key = params.get("token", [None])[0]

        scope["user"] = await get_user_from_token(token_key) if token_key else AnonymousUser()

        return await self.app(scope, receive, send)
