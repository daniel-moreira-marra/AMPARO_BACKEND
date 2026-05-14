from django.apps import AppConfig
from core.events import register_handler

class AccountsConfig(AppConfig):
    name = 'accounts'

    def ready(self):
        # 1. Importamos o módulo inteiro.
        # Agora o Python sabe que 'accounts.events' existe neste escopo.
        import accounts.events 

        # 2. Usamos o prefixo do módulo para referenciar as funções!
        register_handler("user_registered", accounts.events.user_registered_handler)
        register_handler("user_profile_updated", accounts.events.user_profile_updated_handler)
        register_handler("user_password_changed", accounts.events.user_password_changed_handler)
        register_handler("password_reset_requested", accounts.events.password_reset_requested_handler)