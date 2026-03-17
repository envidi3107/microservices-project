from django.db import models

class Recommendation(models.Model):
    customer_id = models.IntegerField()
    book_id = models.IntegerField()
    confidence_score = models.FloatField()
