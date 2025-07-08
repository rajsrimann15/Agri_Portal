from rest_framework import serializers
from .models import Product, Auction

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'category', 'intial_price', 'year']

class AuctionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auction
        fields = ['auction_id', 'bidders', 'current_price', 'created_at', 'last_updated']
