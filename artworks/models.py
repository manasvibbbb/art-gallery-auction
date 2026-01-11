from django.db import models
from accounts.models import CustomUser


class Artwork(models.Model):
    SALE_TYPES = (
        ('auction', 'Auction'),
        ('fixed', 'Fixed Price'),
    )

    artist = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='artworks')
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='artworks/')
    sale_type = models.CharField(max_length=10, choices=SALE_TYPES)
    starting_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fixed_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_sold = models.BooleanField(default=False)

    is_ai_generated = models.BooleanField(
        default=False,
        help_text="Mark if this is AI-generated"
    )
    prompt = models.TextField(
        blank=True,
        help_text="The prompt used to generate this image"
    )
    source_model = models.CharField(
        max_length=100,
        blank=True,
        default="Stable Diffusion API",
        help_text="Which AI model generated this"
    )

    def __str__(self):
        return self.title


    class Meta:
        ordering = ['-created_at']
