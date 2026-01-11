from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import Auction, Bid
from accounts.models import CustomUser
from django.contrib.auth.decorators import login_required
@login_required
def place_bid(request, auction_id):
    auction = get_object_or_404(Auction, pk=auction_id)

    if request.method == 'POST':
        bid_amount = float(request.POST.get('bid_amount', 0))

        if bid_amount > auction.current_bid:
            Bid.objects.create(
                auction=auction,
                bidder=request.user,
                bid_amount=bid_amount
            )
            auction.current_bid = bid_amount
            auction.winner = request.user
            auction.save()
            return redirect('auction_detail', pk=auction.pk)

    return redirect('auction_detail', pk=auction.pk)
@login_required
def auction_list(request):
    auctions = Auction.objects.all()
    return render(request, "auctions/auction_list.html", {"auctions": auctions})
@login_required
def auction_detail(request, pk):
    auction = get_object_or_404(Auction, pk=pk)
    bids = auction.bids.all()
    return render(request, "auctions/auction_detail.html", {"auction": auction, "bids": bids})
@login_required
def winners_list(request):
    winners = Auction.objects.filter(is_active=False, winner__isnull=False)
    return render(request, "auctions/winners_list.html", {"winners": winners})
