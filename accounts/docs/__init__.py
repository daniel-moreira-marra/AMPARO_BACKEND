from .me import me_docs
from .token_by_email import token_by_email_docs
from .signup import signup_docs
from .elder_me import elder_me_get_docs, elder_me_patch_docs, elder_me_put_docs
from .caregiver_me import caregiver_me_get_docs, caregiver_me_patch_docs, caregiver_me_put_docs
from .guardian_me import (
    guardian_me_get_docs,
    guardian_me_patch_docs,
    guardian_me_put_docs,
)
from .professional_me import (
    professional_me_get_docs,
    professional_me_patch_docs,
    professional_me_put_docs,
)
from .institution_me import (
    institution_me_get_docs,
    institution_me_patch_docs,
    institution_me_put_docs,
)

__all__ = [
    "me_docs", 
    "token_by_email_docs", 
    "signup_docs", 

    # ELDER
    "elder_me_get_docs", 
    "elder_me_patch_docs", 
    "elder_me_put_docs", 

    # CAREGIVER
    "caregiver_me_get_docs", 
    "caregiver_me_patch_docs", 
    "caregiver_me_put_docs",

    # GUARDIAN
    "guardian_me_get_docs",
    "guardian_me_patch_docs",
    "guardian_me_put_docs",

    # PROFESSIONAL
    "professional_me_get_docs", 
    "professional_me_patch_docs", 
    "professional_me_put_docs",

    # INSTITUTION
    "institution_me_get_docs", 
    "institution_me_patch_docs", 
    "institution_me_put_docs",
]