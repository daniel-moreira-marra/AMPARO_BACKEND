
from drf_spectacular.utils import extend_schema

from ..serializers import ElderMeSerializer

def elder_me_get_docs():
    """
    Retorna o decorator `extend_schema` pronto para ser aplicado na view ElderMeView.

    Uso:
        @elder_me_get_docs()
        def get(...):
            ...
    """
    return extend_schema(
        tags=["Idosos"],
        summary="Obter meu perfil de idoso",
        responses={200: ElderMeSerializer},
    )

def elder_me_patch_docs():
    """
    Retorna o decorator `extend_schema` pronto para ser aplicado na view ElderMeView.

    Uso:
        @elder_me_patch_docs()
        def patch(...):
            ...
    """
    return extend_schema(
        tags=["Idosos"],
        summary="Atualizar parcialmente meu perfil de idoso",
        request=ElderMeSerializer,
        responses={200: ElderMeSerializer},
    )

def elder_me_put_docs():
    """
    Retorna o decorator `extend_schema` pronto para ser aplicado na view ElderMeView.

    Uso:
        @elder_me_put_docs()
        def put(...):
            ...
    """
    return extend_schema(
        tags=["Idosos"],
        summary="Substituir meu perfil de idoso",
        request=ElderMeSerializer,
        responses={200: ElderMeSerializer},
    )