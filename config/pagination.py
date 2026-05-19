from rest_framework import pagination
from rest_framework.response import Response

from utils.helpers import format_page

class CustomPagination(pagination.PageNumberPagination):
    page_size_query_param = 'limit'
    max_page_size = 100

    def get_paginated_response(self, data):
        page = int(self.request.GET.get('page', 1))
        page_size = int(self.request.GET.get('limit', 5))

        page_details = format_page(page, page_size, self.page.paginator.count) 
        prev = int(page) - 1
        next_page = int(page) + 1 

        return Response({
            'current_page': page,
            'limit': page_size,
            'total_page': page_details['page_count'],
            'count': self.page.paginator.count,
            'results': data,
            'page_details': page_details
        })