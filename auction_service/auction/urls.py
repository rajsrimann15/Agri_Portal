from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.list_products, name='list_products'),
    path('create/', views.create_auction_session, name='create_auction_session'),
    path('bid/', views.place_bid, name='place_bid'),
    path('<uuid:auction_id>/', views.get_auction_details, name='get_auction_details'),
]
