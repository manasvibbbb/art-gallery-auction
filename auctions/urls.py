from django.urls import path
from . import views

urlpatterns = [
    path('', views.auction_list, name='auction_list'),
    path('<int:pk>/', views.auction_detail, name='auction_detail'),
    path('<int:auction_id>/bid/', views.place_bid, name='place_bid'),
    path('winners/', views.winners_list, name='winners_list'),
]
