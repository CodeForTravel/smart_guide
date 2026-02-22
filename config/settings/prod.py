from .base import *

CORS_ALLOWED_ORIGINS = ALLOWED_HOSTS

if DEBUG:
    raise ImportError("DEBUG must be set to False in production environment!")
