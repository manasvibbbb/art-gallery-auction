from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Artwork(models.Model):
    SALE_TYPES = [
        ('auction', 'Live Auction'),
        ('normal', 'Normal Sale'),
    ]

    title = models.CharField(max_length=200)
    artist = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='artworks/')
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sale_type = models.CharField(max_length=10, choices=SALE_TYPES, default='normal')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']


class Rating(models.Model):
    artwork = models.ForeignKey(Artwork, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.artwork.title} - {self.rating} stars"
