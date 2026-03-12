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

# --- S3 Media Storage ---
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME")
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = "public-read"
AWS_QUERYSTRING_AUTH = False

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
