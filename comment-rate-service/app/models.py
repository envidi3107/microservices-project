from django.db import models

class Review(models.Model):
    book_id = models.IntegerField()
    customer_id = models.IntegerField()
    rating = models.IntegerField()
    comment = models.TextField()
