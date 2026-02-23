from django.db import transaction
from django.contrib.auth import get_user_model, password_validation
from typing import Dict, Any

from core.exceptions import domain as domain_exceptions
from core.events import dispatch
from accounts.models import ElderProfile, CaregiverProfile, GuardianProfile, InstitutionProfile, ProfessionalProfile
from accounts.services.user_normalization import normalize_user_contact_address

User = get_user_model()

@transaction.atomic
def register_user(*, data: Dict[str, Any]) -> User:
    """
    Service to register a new user and create their respective profile.
    """
    email = data.get("email")
    password = data.get("password")
    full_name = data.get("full_name")
    normalized_contact_address = normalize_user_contact_address(data, partial=False)
    phone = normalized_contact_address["phone"]
    address_line = data.get("address_line", "")
    city = data.get("city", "")
    state = normalized_contact_address["state"]
    zip_code = normalized_contact_address["zip_code"]
    role = data.get("role")

    if not email:
        raise domain_exceptions.ValidationError("Email is required.", code="missing_email")
    
    if User.objects.filter(email=email).exists():
        raise domain_exceptions.ValidationError("Email already in use.", code="email_exists")

    # Validate password using Django's built-in validators
    try:
        password_validation.validate_password(password)
    except Exception as e:
        raise domain_exceptions.ValidationError(str(e), code="invalid_password")

    user = User.objects.create_user(
        email=email,
        password=password,
        full_name=full_name,
        phone=phone,
        role=role,
        address_line=address_line,
        city=city,
        state=state,
        zip_code=zip_code,
    )

    # Create profile based on role
    if role == "ELDER":
        ElderProfile.objects.create(user=user)
    elif role == "CAREGIVER":
        CaregiverProfile.objects.create(user=user)
    elif role == "GUARDIAN":
        GuardianProfile.objects.create(user=user)
    elif role == "INSTITUTION":
        InstitutionProfile.objects.create(user=user)
    elif role == "PROFESSIONAL":
        ProfessionalProfile.objects.create(user=user)
    else:
        raise domain_exceptions.ValidationError(f"Invalid role: {role}", code="invalid_role")

    dispatch("user_registered", user_id=user.id, email=user.email, role=user.role)

    return user


@transaction.atomic
def update_user_profile(*, user: User, data: Dict[str, Any]) -> User:
    """
    Service to update basic user profile information.
    """
    full_name = data.get("full_name")
    normalized_contact_address = normalize_user_contact_address(data, partial=True)

    phone = normalized_contact_address.get("phone")
    address_line = data.get("address_line")
    city = data.get("city")
    state = normalized_contact_address.get("state")
    zip_code = normalized_contact_address.get("zip_code")

    if full_name is not None:
        user.full_name = full_name
    if phone is not None:
        user.phone = phone
    if address_line is not None:
        user.address_line = address_line
    if city is not None:
        user.city = city
    if state is not None:
        user.state = state
    if zip_code is not None:
        user.zip_code = zip_code

    user.save()

    dispatch("user_profile_updated", user_id=user.id)

    return user


@transaction.atomic
def change_user_password(*, user: User, data: Dict[str, Any]) -> None:
    """
    Service to change a user's password.
    """
    old_password = data.get("old_password")
    new_password = data.get("new_password")

    if not user.check_password(old_password):
        raise domain_exceptions.ValidationError("Incorrect old password.", code="invalid_old_password")

    try:
        password_validation.validate_password(new_password, user=user)
    except Exception as e:
        raise domain_exceptions.ValidationError(str(e), code="invalid_new_password")

    user.set_password(new_password)
    user.save()

    dispatch("user_password_changed", user_id=user.id)
