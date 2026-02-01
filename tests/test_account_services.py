import pytest
from django.contrib.auth import get_user_model
from accounts.services.user_services import register_user, update_user_profile, change_user_password
from core.exceptions import domain as domain_exceptions

User = get_user_model()
pytestmark = pytest.mark.django_db

def test_register_user_success():
    data = {
        "email": "register_test@example.com",
        "password": "StrongPass@123",
        "full_name": "Test User",
        "role": "ELDER"
    }
    user = register_user(data=data)
    
    assert user.id is not None
    assert user.email == "register_test@example.com"
    assert user.role == "ELDER"
    assert hasattr(user, "elder_profile")

def test_register_user_duplicate_email(create_user):
    create_user(email="dup@example.com")
    data = {
        "email": "dup@example.com",
        "password": "StrongPass@123",
        "full_name": "Test User",
        "role": "ELDER"
    }
    
    with pytest.raises(domain_exceptions.ValidationError) as excinfo:
        register_user(data=data)
    assert excinfo.value.code == "email_exists"

def test_update_user_profile_success(create_user):
    user = create_user(full_name="Old Name", phone="123")
    data = {"full_name": "New Name", "phone": "456"}
    
    updated_user = update_user_profile(user=user, data=data)
    
    assert updated_user.full_name == "New Name"
    assert updated_user.phone == "456"

def test_change_user_password_success(create_user):
    user = create_user(password="OldPass@123")
    data = {"old_password": "OldPass@123", "new_password": "NewPass@123"}
    
    change_user_password(user=user, data=data)
    
    assert user.check_password("NewPass@123")

def test_change_user_password_incorrect_old(create_user):
    user = create_user(password="CorrectPass@123")
    data = {"old_password": "WrongPass@123", "new_password": "NewPass@123"}
    
    with pytest.raises(domain_exceptions.ValidationError) as excinfo:
        change_user_password(user=user, data=data)
    assert excinfo.value.code == "invalid_old_password"
