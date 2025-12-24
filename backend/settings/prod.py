from .base import *  # noqa

DEBUG = False

# Em produção, defina exatamente seus domínios
# ALLOWED_HOSTS = ["api.seudominio.com"]

# CORS: defina apenas o domínio do frontend
# CORS_ALLOWED_ORIGINS = ["https://seudominio.com"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB"),
        "USER": os.getenv("POSTGRES_USER"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "HOST": os.getenv("POSTGRES_HOST"),
        "PORT": os.getenv("POSTGRES_PORT"),
    }
}
