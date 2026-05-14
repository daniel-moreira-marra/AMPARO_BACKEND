import os
from .base import *  # noqa

DEBUG = False

ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "*").split(",")

# DEBUG pode ser útil em staging mas deve ser False em prod literal
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# CORS e CSRF
CORS_ALLOW_ALL_ORIGINS = os.getenv("DJANGO_ALLOWED_CORS", "") == "*"
if not CORS_ALLOW_ALL_ORIGINS:
    CORS_ALLOWED_ORIGINS = os.getenv("DJANGO_ALLOWED_CORS", "").split(",")

CSRF_TRUSTED_ORIGINS = [
    origin if origin.startswith("http") else f"http://{origin}"
    for origin in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",") if origin
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB", "amparo_db"),
        "USER": os.getenv("POSTGRES_USER"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "HOST": os.getenv("POSTGRES_HOST"),
        "PORT": os.getenv("POSTGRES_PORT", "5432"),
    }
}

# --- S3 Media Storage ---
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME", "us-east-1")
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

# HARDENING: Desativa Swagger em produção por padrão
ENABLE_SWAGGER = os.getenv("ENABLE_SWAGGER", "False").lower() == "true"

# --- CONFIGURAÇÃO ADICIONADA: Autenticação JWT ---
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}