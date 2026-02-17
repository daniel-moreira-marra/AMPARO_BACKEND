from django.db import transaction
from django.db.models import Q
from django.core.exceptions import PermissionDenied
from typing import Dict, Any

from core.exceptions import domain as domain_exceptions
from accounts.models import (
    ElderProfile, 
    CaregiverProfile,
    ProfessionalProfile,
    GuardianProfile,
    InstitutionProfile
)
from links.models import (
    CaregiverElderLink, 
    ProfessionalElderLink,
    GuardianElderLink,
    InstitutionElderLink
)

# --- Caregiver Link Services ---

def create_caregiver_link(*, caregiver: CaregiverProfile, elder: ElderProfile, **data) -> CaregiverElderLink:
    # Check for existing active or pending links
    existing_link = CaregiverElderLink.objects.filter(
        caregiver=caregiver,
        elder=elder,
        status__in=[CaregiverElderLink.Status.PENDING, CaregiverElderLink.Status.ACTIVE],
        is_active=True
    ).exists()

    if existing_link:
        raise domain_exceptions.ValidationError(
            "Já existe um vínculo pendente ou ativo entre este cuidador e idoso.",
            code="duplicate_link"
        )

    # Force status to PENDING and is_active to True
    data.pop("status", None)
    data.pop("is_active", None)

    return CaregiverElderLink.objects.create(
        caregiver=caregiver,
        elder=elder,
        status=CaregiverElderLink.Status.PENDING,
        is_active=True,
        **data
    )

@transaction.atomic
def respond_to_caregiver_link(*, link_id: int, user: Any, action: str) -> CaregiverElderLink:
    # Lock the row for update to prevent concurrent responses
    try:
        link = CaregiverElderLink.objects.select_for_update().get(id=link_id)
    except CaregiverElderLink.DoesNotExist:
        raise domain_exceptions.NotFoundError(f"Vínculo {link_id} não encontrado.")

    # Permission check: user must be the elder or a guardian of the elder
    is_elder_owner = (user.role == "ELDER" and getattr(user, "elder_profile", None) == link.elder)
    
    is_guardian_owner = False
    if user.role == "GUARDIAN":
        guardian_profile = getattr(user, "guardian_profile", None)
        if guardian_profile:
            is_guardian_owner = link.elder.guardians.filter(id=guardian_profile.id).exists()

    if not (is_elder_owner or is_guardian_owner):
        raise PermissionDenied("Você não tem permissão para responder a este vínculo.")

    # Check status
    if link.status != CaregiverElderLink.Status.PENDING:
        raise domain_exceptions.ConflictError(
            f"Não é possível responder a um vínculo com status {link.status}.",
            code="invalid_link_status"
        )

    if action == "approve":
        link.status = CaregiverElderLink.Status.ACTIVE
        link.is_active = True
    elif action == "reject":
        link.status = CaregiverElderLink.Status.CANCELLED
        link.is_active = False
    else:
        raise domain_exceptions.ValidationError(f"Ação inválida: {action}", code="invalid_action")

    link.save(update_fields=["status", "is_active", "updated_at"])
    return link


# --- Professional Link Services ---

def create_professional_link(*, professional: ProfessionalProfile, elder: ElderProfile, **data) -> ProfessionalElderLink:
    existing_link = ProfessionalElderLink.objects.filter(
        professional=professional,
        elder=elder,
        status__in=[ProfessionalElderLink.Status.PENDING, ProfessionalElderLink.Status.ACTIVE],
        is_active=True
    ).exists()

    if existing_link:
        raise domain_exceptions.ValidationError(
            "Já existe um vínculo pendente ou ativo entre este profissional e idoso.",
            code="duplicate_link"
        )

    data.pop("status", None)
    data.pop("is_active", None)

    return ProfessionalElderLink.objects.create(
        professional=professional,
        elder=elder,
        status=ProfessionalElderLink.Status.PENDING,
        is_active=True,
        **data
    )

@transaction.atomic
def respond_to_professional_link(*, link_id: int, user: Any, action: str) -> ProfessionalElderLink:
    try:
        link = ProfessionalElderLink.objects.select_for_update().get(id=link_id)
    except ProfessionalElderLink.DoesNotExist:
        raise domain_exceptions.NotFoundError(f"Vínculo {link_id} não encontrado.")

    is_elder_owner = (user.role == "ELDER" and getattr(user, "elder_profile", None) == link.elder)
    is_guardian_owner = False
    if user.role == "GUARDIAN":
        guardian_profile = getattr(user, "guardian_profile", None)
        if guardian_profile:
            is_guardian_owner = link.elder.guardians.filter(id=guardian_profile.id).exists()

    if not (is_elder_owner or is_guardian_owner):
        raise PermissionDenied("Você não tem permissão para responder a este vínculo.")

    if link.status != ProfessionalElderLink.Status.PENDING:
        raise domain_exceptions.ConflictError(
            f"Não é possível responder a um vínculo com status {link.status}.",
            code="invalid_link_status"
        )

    if action == "approve":
        link.status = ProfessionalElderLink.Status.ACTIVE
        link.is_active = True
    elif action == "reject":
        link.status = ProfessionalElderLink.Status.CANCELLED
        link.is_active = False
    elif action == "cancel":
         # Logic for cancellation if needed, usually same as reject but different context
         pass
    else:
        # Allow 'reject' or 'approve'
        if action not in ['approve', 'reject']:
             raise domain_exceptions.ValidationError(f"Ação inválida: {action}", code="invalid_action")

    if action == "approve":
        link.status = ProfessionalElderLink.Status.ACTIVE
        link.is_active = True
    elif action == "reject":
        link.status = ProfessionalElderLink.Status.CANCELLED
        link.is_active = False

    link.save(update_fields=["status", "is_active", "updated_at"])
    return link


# --- Guardian Link Services ---

def create_guardian_link(*, guardian: GuardianProfile, elder: ElderProfile, **data) -> GuardianElderLink:
    existing_link = GuardianElderLink.objects.filter(
        guardian=guardian,
        elder=elder,
        status__in=[GuardianElderLink.Status.PENDING, GuardianElderLink.Status.ACTIVE],
        is_active=True
    ).exists()

    if existing_link:
        raise domain_exceptions.ValidationError(
            "Já existe um vínculo pendente ou ativo entre este guardião e idoso.",
            code="duplicate_link"
        )

    data.pop("status", None)
    data.pop("is_active", None)

    return GuardianElderLink.objects.create(
        guardian=guardian,
        elder=elder,
        status=GuardianElderLink.Status.PENDING,
        is_active=True,
        **data
    )

@transaction.atomic
def respond_to_guardian_link(*, link_id: int, user: Any, action: str) -> GuardianElderLink:
    try:
        link = GuardianElderLink.objects.select_for_update().get(id=link_id)
    except GuardianElderLink.DoesNotExist:
        raise domain_exceptions.NotFoundError(f"Vínculo {link_id} não encontrado.")

    # Only the elder can respond to a guardian link (or possibly another guardian, but usually the elder approves their guardians)
    # However, if the elder is under legal guardianship, it might be complex. 
    # For now, let's allow the ELDER to approve their own guardians.
    # If the user is another guardian, should they be able to approve? maybe not.
    if not (user.role == "ELDER" and getattr(user, "elder_profile", None) == link.elder):
        raise PermissionDenied("Você não tem permissão para responder a este vínculo.")

    if link.status != GuardianElderLink.Status.PENDING:
        raise domain_exceptions.ConflictError(
            f"Não é possível responder a um vínculo com status {link.status}.",
            code="invalid_link_status"
        )

    if action == "approve":
        link.status = GuardianElderLink.Status.ACTIVE
        link.is_active = True
    elif action == "reject":
        link.status = GuardianElderLink.Status.CANCELLED
        link.is_active = False
    else:
        raise domain_exceptions.ValidationError(f"Ação inválida: {action}", code="invalid_action")

    link.save(update_fields=["status", "is_active", "updated_at"])
    return link


# --- Institution Link Services ---

def create_institution_link(*, institution: InstitutionProfile, elder: ElderProfile, **data) -> InstitutionElderLink:
    existing_link = InstitutionElderLink.objects.filter(
        institution=institution,
        elder=elder,
        status__in=[InstitutionElderLink.Status.PENDING, InstitutionElderLink.Status.ACTIVE],
        is_active=True
    ).exists()

    if existing_link:
        raise domain_exceptions.ValidationError(
            "Já existe um vínculo pendente ou ativo entre esta instituição e idoso.",
            code="duplicate_link"
        )

    data.pop("status", None)
    data.pop("is_active", None)

    return InstitutionElderLink.objects.create(
        institution=institution,
        elder=elder,
        status=InstitutionElderLink.Status.PENDING,
        is_active=True,
        **data
    )

@transaction.atomic
def respond_to_institution_link(*, link_id: int, user: Any, action: str) -> InstitutionElderLink:
    try:
        link = InstitutionElderLink.objects.select_for_update().get(id=link_id)
    except InstitutionElderLink.DoesNotExist:
        raise domain_exceptions.NotFoundError(f"Vínculo {link_id} não encontrado.")

    is_elder_owner = (user.role == "ELDER" and getattr(user, "elder_profile", None) == link.elder)
    is_guardian_owner = False
    if user.role == "GUARDIAN":
        guardian_profile = getattr(user, "guardian_profile", None)
        if guardian_profile:
            is_guardian_owner = link.elder.guardians.filter(id=guardian_profile.id).exists()

    if not (is_elder_owner or is_guardian_owner):
        raise PermissionDenied("Você não tem permissão para responder a este vínculo.")

    if link.status != InstitutionElderLink.Status.PENDING:
        raise domain_exceptions.ConflictError(
            f"Não é possível responder a um vínculo com status {link.status}.",
            code="invalid_link_status"
        )

    if action == "approve":
        link.status = InstitutionElderLink.Status.ACTIVE
        link.is_active = True
    elif action == "reject":
        link.status = InstitutionElderLink.Status.CANCELLED
        link.is_active = False
    else:
        raise domain_exceptions.ValidationError(f"Ação inválida: {action}", code="invalid_action")

    link.save(update_fields=["status", "is_active", "updated_at"])
    return link
