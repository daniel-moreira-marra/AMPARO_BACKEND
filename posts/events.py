from core.events import dispatch

def post_created_handler(post_id: int, **kwargs):
    # Simple handler for demonstration
    print(f"Event: Post {post_id} created by {kwargs.get('actor_id')}")

def post_deleted_handler(post_id: int, **kwargs):
    # Simple handler for demonstration
    print(f"Event: Post {post_id} deleted by {kwargs.get('actor_id')}")
