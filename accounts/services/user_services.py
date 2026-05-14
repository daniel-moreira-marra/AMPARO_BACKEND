from django.db import transaction
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from typing import Dict, Any

from core.exceptions import domain as domain_exceptions
from core.events import dispatch
from accounts.models import ElderProfile, CaregiverProfile, GuardianProfile, InstitutionProfile, ProfessionalProfile
from accounts.services.user_normalization import normalize_user_contact_address

User = get_user_model()

@transaction.atomic
def register_user(*, data: Dict[str, Any]) -> User:
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
    full_name = data.get("full_name")
    normalized_contact_address = normalize_user_contact_address(data, partial=True)

    phone = normalized_contact_address.get("phone")
    address_line = data.get("address_line")
    city = data.get("city")
    state = normalized_contact_address.get("state")
    zip_code = normalized_contact_address.get("zip_code")

    avatar = data.get("avatar")
    show_email = data.get("show_email")
    show_phone = data.get("show_phone")
    show_links = data.get("show_links")

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
    if avatar is not None:
        user.avatar = avatar
    if show_email is not None:
        user.show_email = show_email
    if show_phone is not None:
        user.show_phone = show_phone
    if show_links is not None:
        user.show_links = show_links

    user.save()
    dispatch("user_profile_updated", user_id=user.id)
    return user

@transaction.atomic
def change_user_password(*, user: User, data: Dict[str, Any]) -> None:
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

# --- FUNÇÕES ADICIONADAS PARA O FLUXO DE "ESQUECI A SENHA" ---

@transaction.atomic
def request_password_reset(*, email: str) -> None:
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        # Segurança: retornar silenciosamente se o e-mail não existir
        return
    
    dispatch("password_reset_requested", user_id=user.id, email=user.email)

@transaction.atomic
def reset_password_with_token(*, uid: str, token: str, new_password: str) -> None:
    try:
        user_id = force_str(urlsafe_base64_decode(uid))
        user = User.objects.get(pk=user_id)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        raise domain_exceptions.ValidationError("Link inválido ou corrompido.", code="invalid_uid")

    if not default_token_generator.check_token(user, token):
        raise domain_exceptions.ValidationError("Link expirado ou token inválido.", code="invalid_token")

    try:
        password_validation.validate_password(new_password, user=user)
    except Exception as e:
        raise domain_exceptions.ValidationError(str(e), code="invalid_password")

    user.set_password(new_password)
    user.save()
    
    dispatch("user_password_changed", user_id=user.id)