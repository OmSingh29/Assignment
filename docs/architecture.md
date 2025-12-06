# Retail Sales Management System – Architecture
Author: Om Singh

## Backend Architecture (Django)
- Django project `core` with app `sales`.
- `Sale` model stores all customer, product, sales, and operational fields from the dataset.
- Services layer (`sales/services/`) contains pure functions for search, filtering, and sorting so logic is reusable and testable.
- Views (`sales/views.py`) orchestrate query building, pagination, and rendering templates.
- Management command `load_sales_data` streams the Excel file into the database without loading the whole file into memory.

## Frontend Architecture (Django Templates + Tailwind CSS)
- Server-rendered templates in `sales/templates/sales/`.
- Base layout `base.html` defines shell and Tailwind setup.
- Page `sales_list.html` implements search bar, filter panel, sorting dropdown, table, and pagination.

## Data Flow
1. Browser sends GET request with query params (search, filters, sort, page).
2. `sales_list` view builds a Django queryset:
   - applies search (name/phone),
   - applies filters (region, gender, age range, etc.),
   - applies sorting (date/quantity/name).
3. Queryset is paginated (10 items per page) and rendered into HTML.
4. User interactions just change query params; no duplicate logic on frontend.

## Folder Structure (Relevant)
- `backend/src/core/` – Django project configuration (settings, urls, wsgi/asgi).
- `backend/src/sales/` – domain logic: models, services, views, templates, management commands.
- `backend/data/` – raw dataset file.
- `docs/` – documentation for architecture and design decisions.
- `frontend/` – placeholder for a decoupled frontend if required in future.

## Module Responsibilities
- `sales/models.py` – database schema + indexes on frequently searched/filtered fields.
- `sales/services/search.py` – full-text search on `customer_name` and `phone_number`.
- `sales/services/filters.py` – composable filters for region, gender, age range, categories, tags, payment method, date range.
- `sales/services/sorting.py` – consistent sorting options.
- `sales/management/commands/load_sales_data.py` – one-time/periodic data ingestion from Excel.
- `sales/views.py` – HTTP handlers combining services and rendering templates.
