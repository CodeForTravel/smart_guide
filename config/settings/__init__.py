from config.settings.base import env
from django.core.exceptions import ImproperlyConfigured


ENV_NAME = env("ENV_NAME")

if ENV_NAME == "PRODUCTION":
    from .prod import *
elif ENV_NAME == "DEVELOPMENT":
    from .dev import *
elif ENV_NAME == "LOCAL":
    from .local import *
else:
    raise ImproperlyConfigured("Plz set proper values to ENV_NAME environment variable.")
