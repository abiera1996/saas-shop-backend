import math
import operator
import uuid
import os, string, random
from datetime import datetime
from django.db.models import Q
from functools import reduce
from django.utils.timezone import now


def id_generator(size=25, chars=string.ascii_lowercase + string.digits):
    """
    Generate random string
    """
    return ''.join(random.choice(chars) for _ in range(size))


def is_numeric(num):
    try:
        float(num)
        return True
    except ValueError:
        return False


def search_result(queryset, search, orm_lookups):
    """
    Alternative function for search queryset
    """
    for bit in search.split():
        or_queries = [Q(**{orm_lookup: bit}) for orm_lookup in orm_lookups]
        queryset = queryset.filter(reduce(operator.or_, or_queries))

    return queryset


def pagination(page_item, current, count):
    pages = round(((count / page_item) + (0 if count % page_item == 0 else 1)))
    start = (page_item * current) - page_item
    end = page_item * current
    if end > count:
        end = (end + count) - end

    if start > end:
        current = 1
        pages = round(((count / page_item) + (0 if count % page_item == 0 else 1)))
        start = (page_item * current) - page_item
        end = page_item * current
        if end > count:
            end = (end + count) - end

    return {
        'start': start,
        'end': end,
        'pages': pages if pages > 1 else 1,
        'page': current,
        'limit': page_item,
        'count': count
    }


def format_listing_data(serializer, queryset, pagination_result):
    if pagination_result:
        return {
            'count': pagination_result['count'],
            'limit': pagination_result['limit'],
            'current_page': pagination_result['page'],
            'total_page': pagination_result['pages'],
            'data': serializer(queryset, many=True).data
        }
    return {
        'count': queryset.count(),
        'data': serializer(queryset, many=True).data
    }
 
def format_page(page, limit, count, span=2): 
    page = int(page)
    limit = int(limit)
    span = int(span)

    offset = (page - 1) * limit 

    try:
        page_count = math.ceil(count / limit)
    except:
        page_count = 1

    has_next = page < page_count
    has_prev = page > 1

    record_from = offset + 1
    record_to = offset + limit if offset + limit <= count else count
    max_range = page + span if page + span <= page_count else page_count
    min_range = page - span if page - span >= 1 else 1

    pages = range(min_range, max_range + 1)
    return {
            "limit": limit,
            "record_count": count,
            "page_count": page_count,
            "record_from": record_from,
            "record_to": record_to,
            "pages": list(pages),
            "page": page,
            "has_next": has_next,
            "has_prev": has_prev,  
            'prev': (int(record_from) - 1) if has_prev else None,
            'next': record_to if has_next else None 
        }


def upload_avatar_to(instance, filename):
    filename_base, filename_ext = os.path.splitext(filename)
    path = instance._meta.model_name
    new_filename = '{}_{}{}'.format(
        uuid.uuid4(),
        now().strftime("%Y%m%d%H%M%S"),
        filename_ext.lower()
    )
    return '{}/{}'.format(path, new_filename)