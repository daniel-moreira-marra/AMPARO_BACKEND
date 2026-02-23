# filepath: /home/euler/AMPARO_BACKEND/posts/docs/__init__.py
from .post_endpoints import (
    schema_posts_list,
    schema_posts_create,
    schema_posts_retrieve,
    schema_posts_update,
    schema_posts_partial_update,
    schema_posts_destroy,
    schema_posts_like_create,
    schema_posts_unlike_delete,
    schema_posts_comment_create,
    schema_posts_comment_list,
    schema_posts_comment_update,
    schema_posts_comment_delete,
)

from .feed_endpoints import (
    schema_feed_list,
)

__all__ = [
    "schema_posts_list",
    "schema_posts_create",
    "schema_posts_retrieve",
    "schema_posts_update",
    "schema_posts_partial_update",
    "schema_posts_destroy",
    "schema_posts_like_create",
    "schema_posts_unlike_delete",
    "schema_posts_comment_create",
    "schema_posts_comment_list",
    "schema_posts_comment_update",
    "schema_posts_comment_delete",
    "schema_feed_list",
]
