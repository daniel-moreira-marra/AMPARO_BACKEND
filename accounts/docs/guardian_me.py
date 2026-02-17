from drf_spectacular.utils import extend_schema

from ..serializers import GuardianMeSerializer

def guardian_me_get_docs():
    """
    Retorna o decorator `extend_schema` pronto para ser aplicado na view GuardianMeView.
    Uso:
        @guardian_me_get_docs()
        def get(...):
            ...
    """
    return extend_schema(
        tags=["Responsáveis"],
        summary="Obter meu perfil de responsável",
        responses={200: GuardianMeSerializer},
    )

def guardian_me_patch_docs():
    """
    Retorna o decorator `extend_schema` pronto para ser aplicado na view GuardianMeView.
    Uso:
        @guardian_me_patch_docs()
        def patch(...):
            ...
    """
    return extend_schema(
        tags=["Responsáveis"],
        summary="Atualizar parcialmente meu perfil de responsável",
        request=GuardianMeSerializer,
        responses={200: GuardianMeSerializer},
    )

def guardian_me_put_docs():
    """
    Retorna o decorator `extend_schema` pronto para ser aplicado na view GuardianMeView.
    Uso:
        @guardian_me_put_docs()
        def put(...):
            ...
    """
    return extend_schema(
        tags=["Responsáveis"],
        summary="Substituir meu perfil de responsável",
        request=GuardianMeSerializer,
        responses={200: GuardianMeSerializer},
    )
