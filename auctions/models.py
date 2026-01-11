from django.db import models
from accounts.models import CustomUser
from artworks.models import Artwork

class Auction(models.Model):
    artwork = models.OneToOneField(Artwork, on_delete=models.CASCADE)
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    current_bid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    winner = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, blank=True, null=True,
                               related_name='won_auctions')
    def __str__(self):
        return f"Auction for {self.artwork.title}"
class Bid(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='bids')
    bidder = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='bids')
    bid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    bid_time = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-bid_time']
        def __str__(self):
            return f"{self.bidder.username} bid ${self.bid_amount} on {self.auction.artwork.title}"
