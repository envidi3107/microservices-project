from django.db import models

class Shipment(models.Model):
    order_id = models.IntegerField()
    tracking_number = models.CharField(max_length=255)
    status = models.CharField(max_length=50, default="Preparing")
