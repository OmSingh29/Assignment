import csv
import io
import os
import tempfile
import requests
from datetime import datetime
from django.core.management.base import BaseCommand
from sales.models import Sale


class Command(BaseCommand):
    help = "Load sales data from a CSV file OR from a direct URL."

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            help="Local CSV file path",
        )
        parser.add_argument(
            "--url",
            type=str,
            help="Direct download URL to CSV file",
        )

    def handle(self, *args, **options):
        file_path = options.get("file")
        url = options.get("url")

        if not file_path and not url:
            self.stderr.write(self.style.ERROR("Provide --file or --url"))
            return

        # ------------------------------------------------------
        # Fetch CSV either from local file OR download from URL
        # ------------------------------------------------------
        if url:
            self.stdout.write(f"Downloading CSV from URL: {url}")

            response = requests.get(url, allow_redirects=True, timeout=60)

            if response.status_code != 200:
                raise Exception(f"Download failed. Status code: {response.status_code}")

            # Check if Google/GitHub returned an HTML page instead of CSV
            content_type = response.headers.get("Content-Type", "")

            if "text/html" in content_type.lower():
                # Also detect HTML content even if Content-Type is wrong
                if response.text.strip().startswith("<!DOCTYPE html") or "<html" in response.text.lower():
                    raise Exception("ERROR: The downloaded content is HTML, not CSV. The link is NOT a direct CSV download URL.")

            # Save temporary CSV file
            temp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
            temp.write(response.content)
            temp.close()

            csv_path = temp.name
            self.stdout.write(f"Downloaded to temp file: {csv_path}")

        else:
            csv_path = file_path

        # ------------------------------------------------------
        # Utility parsing helpers
        # ------------------------------------------------------
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

        # ------------------------------------------------------
        # Insert into DB in batches
        # ------------------------------------------------------
        batch = []
        batch_size = 8000
        total = 0

        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row in reader:
                batch.append(Sale(
                    customer_id=row.get("Customer ID", ""),
                    customer_name=row.get("Customer Name", ""),
                    phone_number=row.get("Phone Number", ""),
                    gender=row.get("Gender", ""),
                    age=parse_int(row.get("Age")),
                    customer_region=row.get("Customer Region", ""),
                    customer_type=row.get("Customer Type", ""),
                    product_id=row.get("Product ID", ""),
                    product_name=row.get("Product Name", ""),
                    brand=row.get("Brand", ""),
                    product_category=row.get("Product Category", ""),
                    tags=row.get("Tags", ""),
                    quantity=parse_int(row.get("Quantity", 0)) or 0,
                    price_per_unit=parse_float(row.get("Price per Unit")),
                    discount_percentage=parse_float(row.get("Discount Percentage")),
                    total_amount=parse_float(row.get("Total Amount")),
                    final_amount=parse_float(row.get("Final Amount")),
                    date=parse_date(row.get("Date")),
                    payment_method=row.get("Payment Method", ""),
                    order_status=row.get("Order Status", ""),
                    delivery_type=row.get("Delivery Type", ""),
                    store_id=row.get("Store ID", ""),
                    store_location=row.get("Store Location", ""),
                    salesperson_id=row.get("Salesperson ID", ""),
                    employee_name=row.get("Employee Name", ""),
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

        # Delete temp file if URL was used
        if url:
            os.remove(csv_path)
