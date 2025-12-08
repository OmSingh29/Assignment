from django.core.paginator import Paginator
from django.shortcuts import render
from .models import Sale
from .services.search import apply_search
from .services.filters import apply_filters, _parse_multi
from .services.sorting import apply_sorting


def sales_list(request):
    # Base queryset (used for both options + data)
    base_qs = Sale.objects.all()
    qs = base_qs

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

    # ---------- dropdown options (distinct values) ----------
    region_options = (
        base_qs.exclude(customer_region="")
        .values_list("customer_region", flat=True)
        .distinct()
        .order_by("customer_region")
    )

    gender_options = (
        base_qs.exclude(gender="")
        .values_list("gender", flat=True)
        .distinct()
        .order_by("gender")
    )

    category_options = (
        base_qs.exclude(product_category="")
        .values_list("product_category", flat=True)
        .distinct()
        .order_by("product_category")
    )

    payment_method_options = (
        base_qs.exclude(payment_method="")
        .values_list("payment_method", flat=True)
        .distinct()
        .order_by("payment_method")
    )

    tag_options = (
        base_qs.exclude(tags="")
        .values_list("tags", flat=True)
        .distinct()
        .order_by("tags")
    )

    # ---------- currently selected values (for keeping state) ----------
    selected_regions = _parse_multi(request.GET, "region")
    selected_genders = _parse_multi(request.GET, "gender")
    selected_categories = _parse_multi(request.GET, "category")
    selected_payment_methods = _parse_multi(request.GET, "payment_method")
    selected_tags = _parse_multi(request.GET, "tags")

    context = {
        "page_obj": page_obj,
        "search_query": search_query,
        "sort_by": sort_by,
        "request": request,  # for reading GET params in template

        # dropdown options
        "region_options": region_options,
        "gender_options": gender_options,
        "category_options": category_options,
        "payment_method_options": payment_method_options,
        "tag_options": tag_options,

        # selected lists (to mark <option selected>)
        "selected_regions": selected_regions,
        "selected_genders": selected_genders,
        "selected_categories": selected_categories,
        "selected_payment_methods": selected_payment_methods,
        "selected_tags": selected_tags,
    }
    return render(request, "sales/sales_list.html", context)
