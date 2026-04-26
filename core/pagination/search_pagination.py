from rest_framework.pagination import LimitOffsetPagination


class SearchPagination(LimitOffsetPagination):
    default_limit = 100
    max_limit = 200
