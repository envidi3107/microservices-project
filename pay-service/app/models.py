from django.db import models


class Payment(models.Model):
    STATUS_CHOICES = [
        ("RESERVED", "Reserved"),
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
        ("CANCELLED", "Cancelled"),
    ]

    order_id = models.IntegerField(unique=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=255, default="Credit Card")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="RESERVED")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment order={self.order_id} [{self.status}]"
