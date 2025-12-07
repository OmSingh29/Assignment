from django.core.management.base import BaseCommand
from sales.models import Sale
from datetime import datetime
import csv
import requests
import tempfile
import os


class Command(BaseCommand):
    help = "Load sales data from a CSV file or a URL."

    def add_arguments(self, parser):
        parser.add_argument("--csv_path", type=str, help="Local CSV file path.")
        parser.add_argument("--url", type=str, help="Remote CSV URL.")

    def handle(self, *args, **options):
        csv_path = options.get("csv_path")
        url = options.get("url")

        if not csv_path and not url:
            self.stderr.write("ERROR: Provide either --csv_path or --url")
            return

        # -----------------------
        # HANDLE URL DOWNLOAD
        # -----------------------
        if url:
            self.stdout.write(self.style.WARNING(f"Downloading CSV from URL: {url}"))

            response = requests.get(url, stream=True)
            response.raise_for_status()

            # Create temp file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                temp_file.write(chunk)
            temp_file.close()

            csv_path = temp_file.name
            self.stdout.write(self.style.SUCCESS(f"Downloaded to temp file: {csv_path}"))

        # -----------------------
        # PARSE CSV
        # -----------------------
        batch = []
        batch_size = 5000
        total = 0

        def parse_int(val):
            try:
                return int(val)
            except:
                return None

        def parse_float(val):
            try:
                return float(val)
            except:
                return 0.0

        def parse_date(val):
            if not val:
                return None
            for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d", "%Y-%m-%d %H:%M:%S"):
                try:
                    return datetime.strptime(val, fmt).date()
                except:
                    continue
            return None

        # Read CSV safely
        with open(csv_path, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)

            for row in reader:
                batch.append(Sale(
                    customer_id=row.get("Customer ID", ""),
                    customer_name=row.get("Customer Name", ""),
                    phone_number=row.get("Phone Number", ""),
                    gender=row.get("Gender") or "",
                    age=parse_int(row.get("Age")),

                    customer_region=row.get("Customer Region") or "",
                    customer_type=row.get("Customer Type") or "",

                    product_id=row.get("Product ID", ""),
                    product_name=row.get("Product Name", ""),
                    brand=row.get("Brand") or "",
                    product_category=row.get("Product Category") or "",
                    tags=row.get("Tags") or "",

                    quantity=parse_int(row.get("Quantity") or 0) or 0,
                    price_per_unit=parse_float(row.get("Price per Unit")),
                    discount_percentage=parse_float(row.get("Discount Percentage")),
                    total_amount=parse_float(row.get("Total Amount")),
                    final_amount=parse_float(row.get("Final Amount")),

                    date=parse_date(row.get("Date")),
                    payment_method=row.get("Payment Method") or "",
                    order_status=row.get("Order Status") or "",
                    delivery_type=row.get("Delivery Type") or "",
                    store_id=row.get("Store ID") or "",
                    store_location=row.get("Store Location") or "",
                    salesperson_id=row.get("Salesperson ID") or "",
                    employee_name=row.get("Employee Name") or "",
                ))

                if len(batch) >= batch_size:
                    Sale.objects.bulk_create(batch)
                    total += len(batch)
                    batch = []
                    self.stdout.write(f"Inserted {total} rows...")

            if batch:
                Sale.objects.bulk_create(batch)
                total += len(batch)

        self.stdout.write(self.style.SUCCESS(f"Import completed. Total rows inserted: {total}"))

        # Cleanup temporary file
        if url:
            os.unlink(csv_path)
