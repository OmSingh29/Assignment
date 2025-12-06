from django.db import models


class Sale(models.Model):
    # Customer fields
    customer_id = models.CharField(max_length=64, db_index=True)
    customer_name = models.CharField(max_length=255, db_index=True)
    phone_number = models.CharField(max_length=32, db_index=True)
    gender = models.CharField(max_length=16, db_index=True)
    age = models.PositiveIntegerField(null=True, blank=True, db_index=True)
    customer_region = models.CharField(max_length=128, db_index=True)
    customer_type = models.CharField(max_length=128, blank=True)

    # Product fields
    product_id = models.CharField(max_length=64)
    product_name = models.CharField(max_length=255)
    brand = models.CharField(max_length=128, blank=True)
    product_category = models.CharField(max_length=128, db_index=True)
    tags = models.TextField(blank=True)

    # Sales fields
    quantity = models.PositiveIntegerField()
    price_per_unit = models.DecimalField(max_digits=12, decimal_places=2)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    total_amount = models.DecimalField(max_digits=14, decimal_places=2)
    final_amount = models.DecimalField(max_digits=14, decimal_places=2)

    # Operational fields
    date = models.DateField(db_index=True)
    payment_method = models.CharField(max_length=64, db_index=True)
    order_status = models.CharField(max_length=64, blank=True)
    delivery_type = models.CharField(max_length=64, blank=True)
    store_id = models.CharField(max_length=64, db_index=True)
    store_location = models.CharField(max_length=128, db_index=True)
    salesperson_id = models.CharField(max_length=64, blank=True)
    employee_name = models.CharField(max_length=255, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["customer_name"]),
            models.Index(fields=["phone_number"]),
            models.Index(fields=["date"]),
            models.Index(fields=["customer_region", "product_category"]),
        ]
        ordering = ["-date", "id"]

    def __str__(self):
        return f"{self.customer_name} - {self.product_name} ({self.date})"
