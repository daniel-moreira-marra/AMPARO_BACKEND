from rest_framework import generics, permissions
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from django.core.cache import cache

from core.cache import generate_feed_cache_key

from ..selectors.feed import get_feed_queryset
from ..serializers import FeedPostSerializer
from ..docs import schema_feed_list
from ..mixins.feed_pagination import FeedPaginationMixin


class FeedListView(FeedPaginationMixin, generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    parser_classes = [JSONParser]
    serializer_class = FeedPostSerializer

    # Importante: como você escolhe dinamicamente, deixe isso explícito
    pagination_class = None

    def get_queryset(self):
        return get_feed_queryset(user=self.request.user)

    def paginate_queryset(self, queryset):
        # Se o mixin não existir/ não fornecer o método, cai pro padrão do DRF
        if not hasattr(self, "get_pagination_class"):
            return super().paginate_queryset(queryset)

        paginator_class = self.get_pagination_class()

        # Permite desativar paginação retornando None no mixin
        if paginator_class is None:
            self._paginator = None
            return None

        self._paginator = paginator_class()
        return self._paginator.paginate_queryset(queryset, self.request, view=self)

    def get_paginated_response(self, data):
        # Se não paginou, devolve lista “crua”
        if not getattr(self, "_paginator", None):
            return Response(data)
        return self._paginator.get_paginated_response(data)

    @schema_feed_list()
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        # 1. Obter parâmetros para a chave
        cursor = request.query_params.get("cursor")
        # Se houver filtros no futuro, eles devem entrar aqui
        extra_params = {} 

        # 2. Gerar chave de cache
        cache_key = generate_feed_cache_key(request.user, cursor, extra_params)

        # 3. Tentar obter do cache
        cached_data = cache.get(cache_key)
        if cached_data is not None:
            # Adicionar um header para identificar cache hit se desejar
            return Response(cached_data, headers={"X-Cache": "HIT"})

        # 4. Se não estiver no cache, executa o fluxo normal
        response = super().list(request, *args, **kwargs)

        # 5. Salvar no cache (apenas se for 200 OK)
        if response.status_code == 200:
            # TTL de 60 segundos como solicitado
            cache.set(cache_key, response.data, timeout=60)
            response["X-Cache"] = "MISS"

        return response
