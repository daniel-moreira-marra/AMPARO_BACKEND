from drf_spectacular.utils import extend_schema
from ..serializers import ProfessionalElderLinkSerializer


def professional_elder_links_list_docs():
    return extend_schema(
        tags=["Profissionais"],
        summary="Listar vínculos do meu perfil profissional com idosos",
        responses={200: ProfessionalElderLinkSerializer(many=True)},
    )


def professional_elder_links_create_docs():
    return extend_schema(
        tags=["Profissionais"],
        summary="Criar vínculo entre meu perfil profissional e um idoso",
        request=ProfessionalElderLinkSerializer,
        responses={201: ProfessionalElderLinkSerializer},
    )


def professional_elder_links_retrieve_docs():
    return extend_schema(
        tags=["Profissionais"],
        summary="Detalhar um vínculo idoso-profissional do meu perfil",
        responses={200: ProfessionalElderLinkSerializer},
    )


def professional_elder_links_patch_docs():
    return extend_schema(
        tags=["Profissionais"],
        summary="Atualizar parcialmente um vínculo idoso-profissional do meu perfil",
        request=ProfessionalElderLinkSerializer,
        responses={200: ProfessionalElderLinkSerializer},
    )


def professional_elder_links_put_docs():
    return extend_schema(
        tags=["Profissionais"],
        summary="Substituir um vínculo idoso-profissional do meu perfil",
        request=ProfessionalElderLinkSerializer,
        responses={200: ProfessionalElderLinkSerializer},
    )


def professional_elder_links_delete_docs():
    return extend_schema(
        tags=["Profissionais"],
        summary="Remover um vínculo idoso-profissional do meu perfil",
        responses={204: None},
    )
