from django.db.models import Q


def _parse_int(value, default=None):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _parse_multi(params, key):
    """
    Reads key from request.GET (a QueryDict) and supports *both*:
    - ?key=North&key=South
    - ?key=North,South
    Returns ["North", "South"] in both cases.
    """
    raw_list = params.getlist(key)
    result = []
    for raw in raw_list:
        if not raw:
            continue
        parts = [p.strip() for p in raw.split(",")]
        for p in parts:
            if p:
                result.append(p)
    return result


def apply_filters(queryset, params):
    # multi-select fields
    regions = _parse_multi(params, "region")
    genders = _parse_multi(params, "gender")
    categories = _parse_multi(params, "category")
    payment_methods = _parse_multi(params, "payment_method")

    # age
    age_min = _parse_int(params.get("age_min"))
    age_max = _parse_int(params.get("age_max"))

    # swap invalid age ranges
    if age_min is not None and age_max is not None and age_min > age_max:
        age_min, age_max = age_max, age_min

    # dates
    date_from = params.get("date_from")
    date_to = params.get("date_to")

    # tags from multi-select / chips => name="tags"
    tag_values = _parse_multi(params, "tags")

    # apply filters
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

    if tag_values:
        q = Q()
        for t in tag_values:
            q |= Q(tags__icontains=t)
        queryset = queryset.filter(q)

    return queryset
