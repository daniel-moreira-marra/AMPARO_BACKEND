from drf_spectacular.utils import extend_schema

from ..serializers import CaregiverElderLinkSerializer


def caregiver_elder_links_list_docs():
    return extend_schema(
        tags=["Cuidadores"],
        summary="Listar vínculos do meu perfil de cuidador com idosos",
        responses={200: CaregiverElderLinkSerializer(many=True)},
    )


def caregiver_elder_links_create_docs():
    return extend_schema(
        tags=["Cuidadores"],
        summary="Criar vínculo entre meu perfil de cuidador e um idoso",
        request=CaregiverElderLinkSerializer,
        responses={201: CaregiverElderLinkSerializer},
    )


def caregiver_elder_links_retrieve_docs():
    return extend_schema(
        tags=["Cuidadores"],
        summary="Detalhar um vínculo idoso-cuidador do meu perfil",
        responses={200: CaregiverElderLinkSerializer},
    )


def caregiver_elder_links_patch_docs():
    return extend_schema(
        tags=["Cuidadores"],
        summary="Atualizar parcialmente um vínculo idoso-cuidador do meu perfil",
        request=CaregiverElderLinkSerializer,
        responses={200: CaregiverElderLinkSerializer},
    )


def caregiver_elder_links_put_docs():
    return extend_schema(
        tags=["Cuidadores"],
        summary="Substituir um vínculo idoso-cuidador do meu perfil",
        request=CaregiverElderLinkSerializer,
        responses={200: CaregiverElderLinkSerializer},
    )


def caregiver_elder_links_delete_docs():
    return extend_schema(
        tags=["Cuidadores"],
        summary="Remover um vínculo idoso-cuidador do meu perfil",
        responses={204: None},
    )
