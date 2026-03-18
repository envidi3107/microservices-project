from django.db import models


class Order(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("CONFIRMED", "Confirmed"),
        ("FAILED", "Failed"),
    ]

    customer_id = models.IntegerField()
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    address = models.CharField(max_length=500, default="")
    payment_method = models.CharField(max_length=100, default="Credit Card")
    shipping_method = models.CharField(max_length=100, default="Standard")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} [{self.status}] - Customer {self.customer_id}"
