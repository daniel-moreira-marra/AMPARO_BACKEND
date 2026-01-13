from drf_spectacular.utils import extend_schema

from ..serializers.professional_me import ProfessionalMeSerializer


def professional_me_get_docs():
    """
    Retorna o decorator `extend_schema` pronto para ser aplicado na view ProfessionalMeView.

    Uso:
        @professional_me_get_docs()
        def get(...):
            ...
    """
    return extend_schema(
        tags=["Profissionais"],
        summary="Obter meu perfil profissional",
        responses={200: ProfessionalMeSerializer},
    )


def professional_me_patch_docs():
    """
    Retorna o decorator `extend_schema` pronto para ser aplicado na view ProfessionalMeView.

    Uso:
        @professional_me_patch_docs()
        def patch(...):
            ...
    """
    return extend_schema(
        tags=["Profissionais"],
        summary="Atualizar parcialmente meu perfil profissional",
        request=ProfessionalMeSerializer,
        responses={200: ProfessionalMeSerializer},
    )


def professional_me_put_docs():
    """
    Retorna o decorator `extend_schema` pronto para ser aplicado na view ProfessionalMeView.

    Uso:
        @professional_me_put_docs()
        def put(...):
            ...
    """
    return extend_schema(
        tags=["Profissionais"],
        summary="Substituir meu perfil profissional",
        request=ProfessionalMeSerializer,
        responses={200: ProfessionalMeSerializer},
    )
