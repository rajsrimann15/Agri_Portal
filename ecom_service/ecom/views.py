from rest_framework import generics, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from .models import Product, Booking
from .serializers import ProductSerializer, BookingSerializer

# Farmer - Create Product
class ProductCreateView(generics.CreateAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()


#  Consumer - List/Search Products
class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'farmer_id']  # Search by product name or farmer_id


#  Consumer - Book a Product
class BookProductView(generics.CreateAPIView):
    serializer_class = BookingSerializer
    queryset = Booking.objects.all()

    def perform_create(self, serializer):
        product = serializer.validated_data['product']
        quantity = serializer.validated_data['quantity']

        if quantity > product.quantity_available:
            raise ValidationError("Not enough stock available.")

        # Reduce product stock
        product.quantity_available -= quantity
        product.save()

        serializer.save()


#  Farmer - Get All Bookings for Their Products
class FarmerBookingsView(APIView):
    def get(self, request):
        farmer_id = request.query_params.get('farmer_id')
        if not farmer_id:
            return Response({"error": "farmer_id query param is required"}, status=400)

        bookings = Booking.objects.filter(product__farmer_id=farmer_id)
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)
