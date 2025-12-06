from django.db.models import Case, When, Value, IntegerField


def apply_sorting(qs, sort_by, search_query=None):
    """
    Apply sorting with priority:
      1. Exact match first (customer_name == search_query)
      2. Then normal sorting rules
    """

    # Add priority so that exact matches appear first
    if search_query:
        qs = qs.annotate(
            exact_match_priority=Case(
                When(customer_name__iexact=search_query, then=Value(0)),
                default=Value(1),
                output_field=IntegerField(),
            )
        )
    else:
        # No search query → normal sorting
        qs = qs.annotate(
            exact_match_priority=Value(1),
        )

    # Apply normal sorting but always prioritize exact matches first
    if sort_by == "date_desc":
        return qs.order_by("exact_match_priority", "-date")

    elif sort_by == "name_asc":
        return qs.order_by("exact_match_priority", "customer_name")

    elif sort_by == "quantity_desc":
        return qs.order_by("exact_match_priority", "-quantity")

    else:
        # Default fallback
        return qs.order_by("exact_match_priority", "-date")
