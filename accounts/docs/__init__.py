from .me import me_docs
from .token_by_email import token_by_email_docs
from .signup import signup_docs
from .elder_me import elder_me_get_docs, elder_me_patch_docs, elder_me_put_docs
from .caregiver_me import caregiver_me_get_docs, caregiver_me_patch_docs, caregiver_me_put_docs
from .guardian_elder_link import guardian_elder_link_docs
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
from .institution_elder_link import (
    institution_elder_links_list_docs,
    institution_elder_links_create_docs,
    institution_elder_links_retrieve_docs,
    institution_elder_links_patch_docs,
    institution_elder_links_put_docs,
    institution_elder_links_delete_docs,
)

from .professional_elder_link import (
    professional_elder_links_list_docs,
    professional_elder_links_create_docs,
    professional_elder_links_retrieve_docs,
    professional_elder_links_patch_docs,
    professional_elder_links_put_docs,
    professional_elder_links_delete_docs,
)

from .caregiver_elder_link import (
    caregiver_elder_links_list_docs,
    caregiver_elder_links_create_docs,
    caregiver_elder_links_retrieve_docs,
    caregiver_elder_links_patch_docs,
    caregiver_elder_links_put_docs,
    caregiver_elder_links_delete_docs,
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
    "caregiver_elder_links_list_docs", 
    "caregiver_elder_links_create_docs", 
    "caregiver_elder_links_retrieve_docs", 
    "caregiver_elder_links_patch_docs", 
    "caregiver_elder_links_put_docs", 
    "caregiver_elder_links_delete_docs",

    # GUARDIAN

    "guardian_elder_link_docs",

    # PROFESSIONAL

    "professional_me_get_docs", 
    "professional_me_patch_docs", 
    "professional_me_put_docs",
    "professional_elder_links_list_docs", 
    "professional_elder_links_create_docs", 
    "professional_elder_links_retrieve_docs", 
    "professional_elder_links_patch_docs", 
    "professional_elder_links_put_docs", 
    "professional_elder_links_delete_docs",

    # INSTITUTION

    "institution_me_get_docs", 
    "institution_me_patch_docs", 
    "institution_me_put_docs",
    "institution_elder_links_list_docs", 
    "institution_elder_links_create_docs", 
    "institution_elder_links_retrieve_docs", 
    "institution_elder_links_patch_docs", 
    "institution_elder_links_put_docs", 
    "institution_elder_links_delete_docs",
]