from rest_framework.pagination import CursorPagination

class TransactionCursorPagination(CursorPagination):
    page_size = 10
    ordering = '-date'
    page_size_query_param = 'page_size'
    max_page_size = 100