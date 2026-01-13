from drf_spectacular.utils import extend_schema

from ..serializers import InstitutionMeSerializer


def institution_me_get_docs():
    """
    Retorna o decorator `extend_schema` pronto para ser aplicado na view InstitutionMeView.

    Uso:
        @institution_me_get_docs()
        def get(...):
            ...
    """
    return extend_schema(
        tags=["Instituições"],
        summary="Obter meu perfil de instituição",
        responses={200: InstitutionMeSerializer},
    )


def institution_me_patch_docs():
    """
    Retorna o decorator `extend_schema` pronto para ser aplicado na view InstitutionMeView.

    Uso:
        @institution_me_patch_docs()
        def patch(...):
            ...
    """
    return extend_schema(
        tags=["Instituições"],
        summary="Atualizar parcialmente meu perfil de instituição",
        request=InstitutionMeSerializer,
        responses={200: InstitutionMeSerializer},
    )


def institution_me_put_docs():
    """
    Retorna o decorator `extend_schema` pronto para ser aplicado na view InstitutionMeView.

    Uso:
        @institution_me_put_docs()
        def put(...):
            ...
    """
    return extend_schema(
        tags=["Instituições"],
        summary="Substituir meu perfil de instituição",
        request=InstitutionMeSerializer,
        responses={200: InstitutionMeSerializer},
    )
