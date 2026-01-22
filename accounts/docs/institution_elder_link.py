from drf_spectacular.utils import extend_schema
from ..serializers import InstitutionElderLinkSerializer


def institution_elder_links_list_docs():
    return extend_schema(
        tags=["Instituições"],
        summary="Listar vínculos da minha instituição com idosos",
        responses={200: InstitutionElderLinkSerializer(many=True)},
    )


def institution_elder_links_create_docs():
    return extend_schema(
        tags=["Instituições"],
        summary="Criar vínculo entre minha instituição e um idoso",
        request=InstitutionElderLinkSerializer,
        responses={201: InstitutionElderLinkSerializer},
    )


def institution_elder_links_retrieve_docs():
    return extend_schema(
        tags=["Instituições"],
        summary="Detalhar um vínculo idoso-instituição da minha instituição",
        responses={200: InstitutionElderLinkSerializer},
    )


def institution_elder_links_patch_docs():
    return extend_schema(
        tags=["Instituições"],
        summary="Atualizar parcialmente um vínculo idoso-instituição da minha instituição",
        request=InstitutionElderLinkSerializer,
        responses={200: InstitutionElderLinkSerializer},
    )


def institution_elder_links_put_docs():
    return extend_schema(
        tags=["Instituições"],
        summary="Substituir um vínculo idoso-instituição da minha instituição",
        request=InstitutionElderLinkSerializer,
        responses={200: InstitutionElderLinkSerializer},
    )


def institution_elder_links_delete_docs():
    return extend_schema(
        tags=["Instituições"],
        summary="Remover um vínculo idoso-instituição da minha instituição",
        responses={204: None},
    )
