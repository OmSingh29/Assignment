from django.core.paginator import Paginator
from django.shortcuts import render
from .models import Sale
from .services.search import apply_search
from .services.filters import apply_filters
from .services.sorting import apply_sorting


def sales_list(request):
    qs = Sale.objects.all()

    # --- search ---
    search_query = request.GET.get("q", "").strip()
    qs = apply_search(qs, search_query)

    # --- filters ---
    qs = apply_filters(qs, request.GET)

    # --- sorting ---
    sort_by = request.GET.get("sort", "date_desc")
    qs = apply_sorting(qs, sort_by, search_query)

    # --- pagination ---
    paginator = Paginator(qs, 10)
    page_number = request.GET.get("page", 1)
    page_obj = paginator.get_page(page_number)

    # ---------- filter options from DB ----------
    # Distinct regions
    regions_qs = (
        Sale.objects.order_by()
        .values_list("customer_region", flat=True)
        .exclude(customer_region__isnull=True)
        .exclude(customer_region="")
        .distinct()
    )
    available_regions = sorted(set(regions_qs))

    # Distinct genders
    genders_qs = (
        Sale.objects.order_by()
        .values_list("gender", flat=True)
        .exclude(gender__isnull=True)
        .exclude(gender="")
        .distinct()
    )
    available_genders = sorted(set(genders_qs))

    # Distinct categories
    categories_qs = (
        Sale.objects.order_by()
        .values_list("product_category", flat=True)
        .exclude(product_category__isnull=True)
        .exclude(product_category="")
        .distinct()
    )
    available_categories = sorted(set(categories_qs))

    # Distinct payment methods
    payment_qs = (
        Sale.objects.order_by()
        .values_list("payment_method", flat=True)
        .exclude(payment_method__isnull=True)
        .exclude(payment_method="")
        .distinct()
    )
    available_payment_methods = sorted(set(payment_qs))

    # Distinct tags (split comma-separated values into individual tags)
    raw_tags_qs = (
        Sale.objects.order_by()
        .values_list("tags", flat=True)
        .exclude(tags__isnull=True)
        .exclude(tags="")
        .distinct()
    )
    tag_set = set()
    for tag_string in raw_tags_qs:
        for part in tag_string.split(","):
            label = part.strip()
            if label:
                tag_set.add(label)
    available_tags = sorted(tag_set)

    # ---------- which filters are currently selected (for checked boxes + labels) ----------
    selected_regions = request.GET.getlist("region")
    selected_genders = request.GET.getlist("gender")
    selected_categories = request.GET.getlist("category")
    selected_payment_methods = request.GET.getlist("payment_method")
    selected_tags = request.GET.getlist("tags")

    context = {
        "page_obj": page_obj,
        "search_query": search_query,
        "sort_by": sort_by,
        "request": request,  # for reading GET params in template

        # dropdown options
        "available_regions": available_regions,
        "available_genders": available_genders,
        "available_categories": available_categories,
        "available_payment_methods": available_payment_methods,
        "available_tags": available_tags,

        # selected values
        "selected_regions": selected_regions,
        "selected_genders": selected_genders,
        "selected_categories": selected_categories,
        "selected_payment_methods": selected_payment_methods,
        "selected_tags": selected_tags,
    }
    return render(request, "sales/sales_list.html", context)
