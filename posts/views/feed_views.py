from rest_framework import generics, permissions
from rest_framework.parsers import JSONParser
from rest_framework.response import Response

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
        return super().get(request, *args, **kwargs)
