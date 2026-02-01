from django.apps import AppConfig

from core.events import register_handler
from .events import user_registered_handler, user_profile_updated_handler, user_password_changed_handler


class AccountsConfig(AppConfig):
    name = 'accounts'

    def ready(self):
        
        register_handler("user_registered", user_registered_handler)
        register_handler("user_profile_updated", user_profile_updated_handler)
        register_handler("user_password_changed", user_password_changed_handler)

