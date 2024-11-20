from rest_framework.pagination import PageNumberPagination as BasePagination


class PageNumberPagination(BasePagination):
    page_size_query_param = 'limit'
