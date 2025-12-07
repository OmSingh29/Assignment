### Overview

Retail Sales Management System built by **Om Singh** for the TruEstate SDE Intern assignment.  
It provides fast search, multi-filtering, sorting, and pagination over a dataset of 1,000,000+ retail sales records.fileciteturn0file0  

### Tech Stack

- **Backend:** Django 5, Django ORM, SQLite (can be swapped for Postgres)
- **Frontend:** Django templates, HTML5, Tailwind CSS
- **Build & Tooling:** Node + Tailwind CLI for CSS, Gunicorn for production server

### Project Structure

```text
root/
├── backend/
│   ├── data/                 # (ignored in Git) large CSV lives here locally
│   └── src/
│       ├── core/             # Django project (settings, urls, wsgi)
│       └── sales/            # App with models, views, services, templates, mgmt cmd
├── frontend/                 # Tailwind build setup (input CSS, npm config)
├── docs/
│   └── architecture.md       # High-level architecture & data flow
├── render.yaml (optional)    # Infra-as-code for Render deployment
├── requirements.txt          # Python dependencies
└── README.md
```

### Local Setup Instructions

1. **Clone the repository**

   ```bash
   git clone https://github.com/OmSingh29/Assignment.git
   cd Assignment
   ```

2. **Create and activate a virtual environment**

   ```bash
   python -m venv venv
   ```

   ```bash
   # On macOS / Linux
   source venv/bin/activate
   ```

   ```bash
   # On Windows (PowerShell)
   venv\Scripts\activate
   ```

3. **Install backend dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Tailwind build (once for local)**

   ```bash
   cd frontend
   npm install
   npm run build
   cd ..
   ```

5. **Apply database migrations**

   ```bash
   cd backend/src
   python manage.py migrate
   ```

6. **Load the sales dataset**

   You can either download the CSV manually into `backend/data/` and pass a file path,  
   or let Django download it from the public GitHub Release URL.

   **Option A — Local file path**

   ```bash
   python manage.py load_sales_data "C:\full\path\to\truestate_assignment.csv"
   ```

   **Option B — Download from GitHub Release URL**

   ```bash
   python manage.py load_sales_data --url "https://github.com/OmSingh29/Assignment/releases/download/v1.0/truestate_assignment.csv"
   ```

   The management command uses chunked streaming and `bulk_create` to efficiently import 1M rows.

7. **Run the development server**

   ```bash
   python manage.py runserver
   ```

   Open http://127.0.0.1:8000/ in your browser.

### Search Implementation Summary

- Search is handled in `sales/services/search.py`.
- Query parameter: `q`.
- Performs **case‑insensitive partial match** on:
  - `customer_name`
  - `phone_number`
- Implemented with Django ORM `icontains` lookups and composed with filters/sorting on the same queryset.

### Filter Implementation Summary

- Filter logic is isolated in `sales/services/filters.py`.
- Reads from `request.GET` and applies composable filters:
  - `region` (multi-select → `customer_region__in`)
  - `gender` (multi-select → `gender__in`)
  - `category` (multi-select → `product_category__in`)
  - `payment_method` (multi-select → `payment_method__in`)
  - `age_min`, `age_max` (validated, swapped if reversed)
  - `date_from`, `date_to` (inclusive range on `date`)
  - `tag` (substring match on `tags` field)
- Safely handles:
  - Empty / missing values
  - Invalid numeric ranges (age swapped if min > max)
  - Combination of many filters at once.

### Sorting Implementation Summary

- Sorting logic lives in `sales/services/sorting.py`.
- Query parameter: `sort`.
- Supported options:
  - `date_desc` (default) – newest transactions first
  - `date_asc` – oldest first
  - `quantity_desc` / `quantity_asc`
  - `name_asc` / `name_desc`
- Sorting always runs **after** search + filters and uses a single `order_by` chain on the queryset.
- For better UX, exact matches on `customer_name` (e.g. `"Neha Khan"`) are surfaced first when a name is searched.

### Pagination Implementation Summary

- Uses Django’s `Paginator` in `sales/views.py`.
- Page size fixed to **10 rows** as required.
- Query parameter: `page`.
- Keeps search, filters, and sort parameters intact when moving across pages by reading from `request.GET`.

### Running in Production (Render)

1. **Build command**

   ```bash
   pip install -r requirements.txt
   ```

   (Plus optional Tailwind build if not checked in.)

2. **Start command**

   ```bash
   cd backend/src && python manage.py migrate --noinput && gunicorn core.wsgi:application --bind 0.0.0.0:$PORT
   ```

3. (Optional) Run dataset import once from the Render shell:

   ```bash
   cd backend/src
   python manage.py load_sales_data --url "https://github.com/OmSingh29/Assignment/releases/download/v1.0/truestate_assignment.csv"
   ```

### Notes

- Large CSV (≈224 MB, 1M rows) is **not** stored in the repo; instead it is downloaded at import time or stored locally under `backend/data/`.
- All search, filter, sort, and pagination logic is implemented on the backend using Django ORM so the UI remains responsive even on large datasets.
