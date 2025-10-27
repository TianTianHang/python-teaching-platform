# pagination.py
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10                     # 默认每页数量
    page_size_query_param = 'page_size'  # 客户端可通过 ?page_size=20 指定
    max_page_size = 100                # 限制最大每页数量
    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'page_size':self.get_page_size(self.request),
            'results': data,
        })