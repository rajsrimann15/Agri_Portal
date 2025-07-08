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

    # Check if 10 bids reached
    if StagingBid.objects.filter(auction=auction).count() >= 2:
        compute_and_flush_bids(auction)

    return Response({'message': 'Bid submitted'})


def compute_and_flush_bids(auction):
    staging_bids = StagingBid.objects.filter(auction=auction)

    # Step 1: Compute averages
    product_price_map = {}
    farmer_bid_map = {}

    for bid in staging_bids:
        pid = str(bid.product.id)
        fid = str(bid.farmer_id)

        # For product → average price
        product_price_map.setdefault(pid, []).append(bid.price)

        # For farmer → what product they bid for
        farmer_bid_map.setdefault(fid, {})[pid] = bid.price

    # Compute final prices
    current_price = {
        pid: sum(prices)/len(prices) for pid, prices in product_price_map.items()
    }

    # Update Auction
    auction.bidders.update(farmer_bid_map)
    auction.current_price.update(current_price)
    auction.save()

    # Clear staging bids
    staging_bids.delete()


@api_view(['GET'])
def get_auction_details(request, auction_id):
    auction = get_object_or_404(Auction, auction_id=auction_id)
    serializer = AuctionSerializer(auction)
    return Response(serializer.data)