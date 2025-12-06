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

    context = {
        "page_obj": page_obj,
        "search_query": search_query,
        "sort_by": sort_by,
        "request": request,  # for reading GET params in template
    }
    return render(request, "sales/sales_list.html", context)
