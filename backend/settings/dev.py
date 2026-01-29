from .base import *  # noqa
from datetime import timedelta

DEBUG = True

# React local (ajuste portas se necessário)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Em dev, é comum facilitar o acesso ao Swagger
REST_FRAMEWORK["DEFAULT_PERMISSION_CLASSES"] = (
    "rest_framework.permissions.AllowAny",
)


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("LOCAL_POSTGRES_DB"),
        "USER": os.getenv("LOCAL_POSTGRES_USER"),
        "PASSWORD": os.getenv("LOCAL_POSTGRES_PASSWORD"),
        "HOST": os.getenv("LOCAL_POSTGRES_HOST"),
        "PORT": os.getenv("LOCAL_POSTGRES_PORT"),
    }
}

SIMPLE_JWT = {
        "ACCESS_TOKEN_LIFETIME": timedelta(days=365 * 10),  # 10 anos 😄
        "REFRESH_TOKEN_LIFETIME": timedelta(days=365 * 10),
        "ROTATE_REFRESH_TOKENS": False,
        "BLACKLIST_AFTER_ROTATION": False,
}


