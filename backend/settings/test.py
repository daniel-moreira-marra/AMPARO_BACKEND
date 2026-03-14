from .base import *  # noqa
from datetime import timedelta

# Banco em memória — rápido, isolado, sem dependência externa
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Permissões abertas para facilitar os testes
REST_FRAMEWORK["DEFAULT_PERMISSION_CLASSES"] = (
    "rest_framework.permissions.AllowAny",
)

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": __import__("datetime").timedelta(days=365 * 10),
    "REFRESH_TOKEN_LIFETIME": __import__("datetime").timedelta(days=365 * 10),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
}

# Desativa o backend de S3 — testes não devem fazer upload real
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.InMemoryStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}
