from django.db.models import Q


def apply_search(queryset, query: str):
    """
    Full-text search on customer name and phone number.
    Case-insensitive and safe to call with empty query.
    """
    if not query:
        return queryset

    query = query.strip()
    if not query:
        return queryset

    return queryset.filter(
        Q(customer_name__icontains=query)
        | Q(phone_number__icontains=query)
    )
