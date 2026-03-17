from django.db import models

class Order(models.Model):
    customer_id = models.IntegerField()
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=50, default="Pending")
