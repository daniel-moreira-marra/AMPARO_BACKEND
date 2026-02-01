from django.apps import AppConfig


class PostsConfig(AppConfig):
    name = 'posts'

    def ready(self):
        from core.events import register_handler
        from .events import post_created_handler, post_deleted_handler
        
        register_handler("post_created", post_created_handler)
        register_handler("post_deleted", post_deleted_handler)

