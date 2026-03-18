from django.db import models


class Shipment(models.Model):
    STATUS_CHOICES = [
        ("RESERVED", "Reserved"),
        ("CONFIRMED", "Confirmed"),
        ("CANCELLED", "Cancelled"),
    ]

    order_id = models.IntegerField(unique=True)
    address = models.CharField(max_length=500, default="")
    shipping_method = models.CharField(max_length=100, default="Standard")
    tracking_number = models.CharField(max_length=255, blank=True, default="")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="RESERVED")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Shipment order={self.order_id} [{self.status}]"
