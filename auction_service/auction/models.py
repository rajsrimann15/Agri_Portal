import uuid
from django.db import models

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('millet', 'Millet'),
        ('vegetable', 'Vegetable'),
        ('fruit', 'Fruit'),
    ]
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    intial_price = models.FloatField()
    year = models.IntegerField()

    def __str__(self):
        return self.name


class Auction(models.Model):
    auction_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    bidders = models.JSONField(default=dict)         # Format: {farmer_id: {product_id: price}}
    current_price = models.JSONField(default=dict)   # Format: {product_id: average_price}
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Auction {self.auction_id}"
