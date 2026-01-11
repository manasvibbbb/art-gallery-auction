from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from .models import CartItem, CustomArtOrder, Order, Payment
from artworks.models import Artwork
from accounts.models import CustomUser


# ============= SHOPPING CART VIEWS =============

@login_required
def add_to_cart(request, pk):
    """Add artwork to shopping cart"""
    artwork = get_object_or_404(Artwork, pk=pk)

    # Check if item already in cart
    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        artwork=artwork,
        defaults={'quantity': 1}
    )

    # If already in cart, increase quantity
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('view_cart')


@login_required
def view_cart(request):
    """Display shopping cart with total calculation"""
    cart_items = CartItem.objects.filter(user=request.user)

    # Calculate total
    total = sum(
        (item.artwork.price or 0) * item.quantity
        for item in cart_items
    )

    return render(request, 'payments/cart.html', {
        'cart_items': cart_items,
        'total': total,
    })


@login_required
def remove_from_cart(request, item_id):
    """Remove item from shopping cart"""
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    cart_item.delete()
    return redirect('view_cart')


# ============= CUSTOM ART ORDER VIEWS =============

@login_required
def customize_art(request):
    """Create custom art order request"""
    if request.method == 'POST':
        title = request.POST.get('title', '')
        art_type = request.POST.get('art_type', '')
        description = request.POST.get('description', '')
        length = request.POST.get('length', '')
        budget = request.POST.get('budget', 0)
        artist_request = request.POST.get('artist_request', '')
        assigned_artist_id = request.POST.get('assigned_artist')

        # Create custom art order
        custom_order = CustomArtOrder.objects.create(
            user=request.user,
            title=title,
            art_type=art_type,
            description=description,
            length=length,
            budget=budget,
            artist_request=artist_request,
            status='pending',
        )

        # Assign artist if selected
        if assigned_artist_id:
            try:
                artist = CustomUser.objects.get(pk=assigned_artist_id, is_staff=True)
                custom_order.assigned_artist = artist
                custom_order.status = 'accepted'
                custom_order.save()
            except CustomUser.DoesNotExist:
                pass

        return redirect('custom_order_detail', pk=custom_order.pk)

    # GET request - show form with available artists
    artists = CustomUser.objects.filter(is_staff=True)
    return render(request, 'payments/customize_art.html', {
        'artists': artists,
    })


@login_required
def custom_order_detail(request, pk):
    """Display custom order details"""
    order = get_object_or_404(CustomArtOrder, pk=pk, user=request.user)
    return render(request, 'payments/custom_order_detail.html', {'order': order})


@login_required
def my_custom_orders(request):
    """Display all custom orders by user"""
    orders = CustomArtOrder.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'payments/my_custom_orders.html', {'orders': orders})


@login_required
def artist_update_order_status(request, pk):
    """Allow assigned artist to update custom order status"""
    order = get_object_or_404(
        CustomArtOrder,
        pk=pk,
        assigned_artist=request.user,
    )

    if request.method == 'POST':
        new_status = request.POST.get('status')
        valid_statuses = ['pending', 'accepted', 'in_progress', 'completed', 'rejected']

        if new_status in valid_statuses:
            order.status = new_status

            # Set completion timestamp when marked as completed
            if new_status == 'completed':
                order.completed_at = timezone.now()

            order.save()
            return redirect('custom_order_detail', pk=order.pk)

    return render(request, 'payments/artist_update_order_status.html', {'order': order})


# ============= REGULAR ORDER & PAYMENT VIEWS =============

@login_required
def checkout(request, pk):
    """Checkout for single artwork purchase"""
    artwork = get_object_or_404(Artwork, pk=pk)

    if request.method == 'POST':
        # Create order
        order = Order.objects.create(
            buyer=request.user,
            artwork=artwork,
            amount=artwork.price or 0,
            status='pending',
        )
        return redirect('payment', order_id=order.pk)

    return render(request, 'payments/checkout.html', {'artwork': artwork})


@login_required
def payment(request, order_id):
    """Process payment for order"""
    order = get_object_or_404(Order, pk=order_id, buyer=request.user)

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method', 'stripe')
        payment_id = request.POST.get('payment_id', f'test_{order.id}')

        # Create payment record
        Payment.objects.create(
            order=order,
            payment_method=payment_method,
            payment_id=payment_id,
            amount_paid=order.amount,
            is_successful=True,
        )

        # Update order status
        order.status = 'completed'
        order.save()

        return redirect('payment_success', payment_id=order.pk)

    return render(request, 'payments/payment.html', {'order': order})


@login_required
def payment_success(request, payment_id):
    """Display payment success page"""
    payment = get_object_or_404(Payment, pk=payment_id)
    return render(request, 'payments/success.html', {'payment': payment})


@login_required
def my_orders(request):
    """Display all orders by user"""
    orders = Order.objects.filter(buyer=request.user).order_by('-created_at')
    return render(request, 'payments/my_orders.html', {'orders': orders})
