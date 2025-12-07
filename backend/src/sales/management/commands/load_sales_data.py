from django.core.management.base import BaseCommand
from sales.models import Sale
from datetime import datetime
from django.db import transaction

import csv
import io
import re
import requests


class Command(BaseCommand):
    help = "Load sales data from a CSV file (local path or URL including Google Drive)."

    def add_arguments(self, parser):
        parser.add_argument("csv_path", nargs="?", type=str)
        parser.add_argument("--url", type=str, help="CSV file URL")

    def download_from_google_drive(self, url):
        file_id = None

        patterns = [
            r"/d/([^/]+)/",
            r"id=([^&]+)",
        ]

        for p in patterns:
            m = re.search(p, url)
            if m:
                file_id = m.group(1)
                break

        if not file_id:
            raise Exception("Google Drive file ID not found in URL.")

        session = requests.Session()
        base_url = "https://drive.google.com/uc?export=download"

        response = session.get(base_url, params={"id": file_id}, stream=True)
        token = None

        for key, value in response.cookies.items():
            if key.startswith("download_warning"):
                token = value

        if token:
            response = session.get(
                base_url, params={"id": file_id, "confirm": token}, stream=True
            )

        response.raise_for_status()
        encoding = response.apparent_encoding or "utf-8"
        return io.TextIOWrapper(response.raw, encoding=encoding)

    def handle(self, *args, **opts):
        path = opts.get("csv_path")
        url = opts.get("url")

        if not path and not url:
            self.stderr.write("Provide a local path OR --url")
            return

        if Sale.objects.exists():
            self.stdout.write("Data already loaded. Skipping.")
            return

        # select input source
        if url:
            if "drive.google.com" in url:
                stream = self.download_from_google_drive(url)
            else:
                r = requests.get(url, stream=True)
                r.raise_for_status()
                stream = io.TextIOWrapper(r.raw, encoding="utf-8")

            reader = csv.DictReader(stream)

        else:
            f = open(path, "r", encoding="utf-8")
            reader = csv.DictReader(f)

        def parse_int(v):
            try:
                return int(v)
            except:
                return None

        def parse_float(v):
            try:
                return float(v)
            except:
                return 0.0

        def parse_date(v):
            if not v:
                return None
            for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%Y/%m/%d", "%Y-%m-%d %H:%M:%S"):
                try:
                    return datetime.strptime(v, fmt).date()
                except:
                    pass
            return None

        batch, batch_size, total = [], 5000, 0

        @transaction.atomic
        def flush():
            nonlocal total, batch
            if batch:
                Sale.objects.bulk_create(batch)
                total += len(batch)
                batch = []

        for row in reader:
            batch.append(
                Sale(
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
                )
            )

            if len(batch) >= batch_size:
                flush()

        flush()
        self.stdout.write(f"Import completed. Rows inserted: {total}")
