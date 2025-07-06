from django.urls import path
from .views import (
    ProductCreateView,
    ProductListView,
    BookProductView,
    FarmerBookingsView,
)

urlpatterns = [
    path('products/create/', ProductCreateView.as_view()),
    path('products/', ProductListView.as_view()),
    path('products/book/', BookProductView.as_view()),
    path('farmer/bookings/', FarmerBookingsView.as_view()),
]
