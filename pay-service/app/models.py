from django.db import models

class Payment(models.Model):
    order_id = models.IntegerField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=255)
    status = models.CharField(max_length=50, default="Unpaid")
