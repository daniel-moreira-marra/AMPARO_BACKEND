from rest_framework.pagination import CursorPagination


class FeedCursorPagination(CursorPagination):
    page_size = 20
    # published_at is always set for PUBLISHED posts (feed selector filters by status=PUBLISHED)
    # Use id as tiebreaker since it is unique and monotonically increasing
    ordering = ("-published_at", "-id")
    cursor_query_param = "cursor"
