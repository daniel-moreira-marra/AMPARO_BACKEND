from rest_framework.pagination import CursorPagination


class FeedCursorPagination(CursorPagination):
    page_size = 20
    # Usar created_at pois published_at pode ser NULL, o que causa erro no CursorPagination
    ordering = "-created_at"
    cursor_query_param = "cursor"
