from drf_spectacular.utils import extend_schema, extend_schema_view

from ..serializers.guardian_elder_link import GuardianElderLinkSerializer

def guardian_elder_link_docs():
    """
    Retorna o decorator `extend_schema` pronto para ser aplicado na view GuardianElderLinkViewSet.

    Uso:
        @guardian_elder_link_docs()
        def list(...):
            ...
    """
    return extend_schema_view(
        list=extend_schema(tags=["Responsáveis"], summary="Listar meus vínculos com idosos"),
        create=extend_schema(tags=["Responsáveis"], summary="Criar vínculo com um idoso"),
        retrieve=extend_schema(tags=["Responsáveis"], summary="Detalhar um vínculo"),
        partial_update=extend_schema(tags=["Responsáveis"], summary="Atualizar parcialmente um vínculo"),
        update=extend_schema(tags=["Responsáveis"], summary="Atualizar um vínculo"),
        destroy=extend_schema(tags=["Responsáveis"], summary="Remover um vínculo"),
    )