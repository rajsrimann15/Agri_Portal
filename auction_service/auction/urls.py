from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.list_products),
    path('create/', views.create_auction_session),
    path('bid/', views.place_bid),
    path('<uuid:auction_id>/', views.get_auction_details),
]
