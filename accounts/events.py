from core.events import dispatch

def user_registered_handler(user_id: int, **kwargs):
    print(f"Event: User {user_id} ({kwargs.get('email')}) registered as {kwargs.get('role')}.")

def user_profile_updated_handler(user_id: int, **kwargs):
    print(f"Event: User {user_id} profile updated.")

def user_password_changed_handler(user_id: int, **kwargs):
    print(f"Event: User {user_id} password changed.")
