from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Product, Auction
from .serializers import ProductSerializer, AuctionSerializer
from . import bid_buffer
from django.utils.timezone import now
import uuid


# 1. Admin creates an auction session
@api_view(['POST'])
def create_auction_session(request):
    auction = Auction.objects.create()
    return Response({
        "auction_id": auction.auction_id,
        "message": "Auction session created"
    }, status=201)


# 2. Farmer views products
@api_view(['GET'])
def list_products(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


# 3. Farmer places bid
@api_view(['POST'])
def place_bid(request):
    auction_id = request.data.get('auction_id')
    product_id = request.data.get('product_id')
    farmer_id = str(request.data.get('farmer_id'))
    price = float(request.data.get('price'))

    if not (auction_id and product_id and farmer_id and price):
        return Response({'error': 'Missing fields'}, status=400)

    try:
        auction = Auction.objects.get(auction_id=auction_id)
    except Auction.DoesNotExist:
        return Response({'error': 'Invalid auction ID'}, status=404)

    bid_buffer.add_bid(auction_id, product_id, farmer_id, price)

    if bid_buffer.is_full(auction_id):
        compute_and_update_auction(auction_id, auction)

    return Response({'message': 'Bid recorded in buffer'}, status=200)


# 4. Process bids and update Auction DB
def compute_and_update_auction(auction_id, auction_obj):
    all_bids = bid_buffer.get_buffer(auction_id)

    # Step 1: group by product and compute average
    price_map = {}     # {product_id: [prices]}
    bidder_map = {}    # {farmer_id: {product_id: price}}

    for product_id, farmer_id, price in all_bids:
        price_map.setdefault(product_id, []).append(price)
        bidder_map.setdefault(farmer_id, {})[product_id] = price

    computed_prices = {
        str(pid): sum(prices) / len(prices) for pid, prices in price_map.items()
    }

    # Step 2: update auction DB
    auction_obj.bidders.update(bidder_map)
    auction_obj.current_price.update(computed_prices)
    auction_obj.save()

    # Step 3: clear hashset
    bid_buffer.clear_buffer(auction_id)



# 5. Get auction details
@api_view(['GET'])
def get_auction_details(request, auction_id):
    auction = get_object_or_404(Auction, auction_id=auction_id)
    serializer = AuctionSerializer(auction)
    return Response(serializer.data, status=200)