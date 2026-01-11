from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('buyer', 'Buyer'),
        ('artist', 'Artist'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='buyer')
    bio = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)


    def __str__(self):
        return self.username

class ArtistRating(models.Model):
    artist = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='artist_ratings')
    rater = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='ratings_given')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 stars
    review = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

