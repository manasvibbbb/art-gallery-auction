from django.db import models
from accounts.models import CustomUser


class Artwork(models.Model):
    SALE_TYPES = [
        ('auction', 'Live Auction'),
        ('normal', 'Normal Sale'),
    ]

    title = models.CharField(max_length=200)
    artist = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='artworks/')
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_type = models.CharField(max_length=10, choices=SALE_TYPES, default='normal')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']
