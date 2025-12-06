def _parse_int(value, default=None):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _clean_multi(values):
    """
    Remove empty strings from multi-select lists like ["", "North"] -> ["North"].
    """
    return [v for v in values if v]


def apply_filters(queryset, params):
    """
    params is request.GET (a QueryDict).
    Supports:
      - region (multi)
      - gender (multi)
      - category (multi)
      - payment_method (multi)
      - age_min / age_max
      - date_from / date_to
      - tag(s) (single text: partial match in tags field)
    """

    regions = _clean_multi(params.getlist("region"))
    genders = _clean_multi(params.getlist("gender"))
    categories = _clean_multi(params.getlist("category"))
    payment_methods = _clean_multi(params.getlist("payment_method"))

    age_min = _parse_int(params.get("age_min"))
    age_max = _parse_int(params.get("age_max"))

    # If both present but reversed, silently swap -> handles invalid numeric ranges
    if age_min is not None and age_max is not None and age_min > age_max:
        age_min, age_max = age_max, age_min

    date_from = params.get("date_from") or None
    date_to = params.get("date_to") or None

    # Support both `tag` and `tags` query params
    tag = params.get("tag") or params.get("tags")
    if tag is not None:
        tag = tag.strip()
        if not tag:
            tag = None

    if regions:
        queryset = queryset.filter(customer_region__in=regions)

    if genders:
        queryset = queryset.filter(gender__in=genders)

    if categories:
        queryset = queryset.filter(product_category__in=categories)

    if payment_methods:
        queryset = queryset.filter(payment_method__in=payment_methods)

    if age_min is not None:
        queryset = queryset.filter(age__gte=age_min)

    if age_max is not None:
        queryset = queryset.filter(age__lte=age_max)

    if date_from:
        queryset = queryset.filter(date__gte=date_from)

    if date_to:
        queryset = queryset.filter(date__lte=date_to)

    if tag:
        queryset = queryset.filter(tags__icontains=tag)

    return queryset
