from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Product, Auction
from .serializers import ProductSerializer, AuctionSerializer
from django.utils.timezone import now
from .models import StagingBid


@api_view(['POST'])
def create_auction_session(request):
    auction = Auction.objects.create()
    return Response({
        "auction_id": auction.auction_id,
        "message": "Auction session created"
    })


@api_view(['GET'])
def list_products(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def place_bid(request):
    auction_id = request.data.get('auction_id')
    product_id = request.data.get('product_id')
    farmer_id = request.data.get('farmer_id')
    price = request.data.get('price')

    if not (auction_id and product_id and farmer_id and price):
        return Response({'error': 'Missing fields'}, status=400)

    auction = get_object_or_404(Auction, auction_id=auction_id)
    product = get_object_or_404(Product, id=product_id)

    # Save to staging DB
    StagingBid.objects.create(
        auction=auction,
        product=product,
        farmer_id=farmer_id,
        price=price
    )
    # Check if this product under this auction has ≥ 2 bids
    bid_count = StagingBid.objects.filter(auction=auction, product=product).count()
    if bid_count >= 2:
        compute_and_flush_bids(auction, product)

    return Response({'message': 'Bid submitted'})


def compute_and_flush_bids(auction, product):
    staging_bids = StagingBid.objects.filter(auction=auction, product=product)

    product_price_list = []
    farmer_bid_map = {}

    for bid in staging_bids:
        fid = str(bid.farmer_id)
        product_price_list.append(bid.price)

        # Track what this farmer bid for this product
        if fid not in farmer_bid_map:
            farmer_bid_map[fid] = {}
        farmer_bid_map[fid][str(product.id)] = bid.price

    # Compute average price for the product
    current_price = sum(product_price_list) / len(product_price_list)

    # Update auction current_price and bidders maps
    auction.current_price = auction.current_price or {}
    auction.bidders = auction.bidders or {}

    auction.current_price[str(product.id)] = current_price

    # Merge bidder entries
    for fid, prod_map in farmer_bid_map.items():
        if fid not in auction.bidders:
            auction.bidders[fid] = {}
        auction.bidders[fid].update(prod_map)

    auction.save()

    # Clear staging bids for this product
    staging_bids.delete()



@api_view(['GET'])
def get_auction_details(request, auction_id):
    auction = get_object_or_404(Auction, auction_id=auction_id)
    serializer = AuctionSerializer(auction)
    return Response(serializer.data)