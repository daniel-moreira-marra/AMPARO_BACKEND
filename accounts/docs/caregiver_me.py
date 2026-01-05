from drf_spectacular.utils import extend_schema

from ..serializers import CaregiverMeSerializer

def caregiver_me_get_docs():
    """
    Retorna o decorator `extend_schema` pronto para ser aplicado na view CaregiverMeView.
    Uso:
        @caregiver_me_get_docs()
        def get(...):
            ...
    """
    return extend_schema(
        tags=["Cuidadores"],
        summary="Obter meu perfil de cuidador",
        responses={200: CaregiverMeSerializer},
    )

def caregiver_me_patch_docs():
    """
    Retorna o decorator `extend_schema` pronto para ser aplicado na view CaregiverMeView.
    Uso:
        @caregiver_me_patch_docs()
        def patch(...):
            ...
    """
    return extend_schema(
        tags=["Cuidadores"],
        summary="Atualizar parcialmente meu perfil de cuidador",
        request=CaregiverMeSerializer,
        responses={200: CaregiverMeSerializer},
    )

def caregiver_me_put_docs():
    """
    Retorna o decorator `extend_schema` pronto para ser aplicado na view CaregiverMeView.
    Uso:
        @caregiver_me_put_docs()
        def put(...):
            ...
    """
    return extend_schema(
        tags=["Cuidadores"],
        summary="Substituir meu perfil de cuidador",
        request=CaregiverMeSerializer,
        responses={200: CaregiverMeSerializer},
    )