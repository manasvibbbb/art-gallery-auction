from django.db import models
from accounts.models import CustomUser
from artworks.models import Artwork

class CartItem(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='cart_items')
    artwork = models.ForeignKey(Artwork, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.user.username} - {self.artwork.title}"
class CustomArtOrder(models.Model):
    ART_TYPES = (
        ('oil', 'Oil Painting'),
        ('water', 'Watercolor Painting'),
        ('acrylic', 'Acrylic Painting'),
        ('digital', 'Digital Art'),
        ('charcoal', 'Charcoal Drawing'),
        ('pencil', 'Pencil Sketch'),
        ('sculpture', 'Sculpture'),
        ('other', 'Other'),
    )
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='custom_orders')
    title = models.CharField(max_length=200)
    art_type = models.CharField(max_length=20, choices=ART_TYPES)
    description = models.TextField()
    length = models.CharField(max_length=100, help_text="e.g., 24x36 inches")
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    artist_request = models.TextField(blank=True, null=True, help_text="Any specific artist preference")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    def __str__(self):
        return f"{self.title} - {self.user.username}"
class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    buyer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='orders')
    artwork = models.ForeignKey(Artwork, on_delete=models.CASCADE, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    def __str__(self):
        return f"Order {self.id} - {self.artwork.title if self.artwork else 'N/A'}"
class Payment(models.Model):
    PAYMENT_METHODS = (
        ('stripe', 'Stripe'),
        ('paypal', 'PayPal'),
    )
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    payment_id = models.CharField(max_length=200, unique=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    is_successful = models.BooleanField(default=False)
    def __str__(self):
        return f"Payment for Order {self.order.id}"
