from core.pagination import FeedCursorPagination, FeedPagePagination

class FeedPaginationMixin:
    """
    Usa CursorPagination por padrão.
    Se 'page' estiver presente, usa PageNumberPagination.
    """

    def get_pagination_class(self):
        # fallback quando quiser page=2
        if "page" in self.request.query_params:
            return FeedPagePagination
        # padrão: cursor
        return FeedCursorPagination