from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.db.models import Avg

from .models import CustomUser, ArtistRating
from .forms import ArtistRatingForm

from artworks.models import Artwork
from auctions.models import Auction


@login_required
def artist_dashboard(request):
    """Artist dashboard showing their artworks and auction stats"""

    # ✅ FIX: use request.user (artist was undefined before)
    artworks = Artwork.objects.filter(artist=request.user)
    auctions = Auction.objects.filter(artwork__artist=request.user)

    context = {
        'artworks': artworks,
        'auctions': auctions,
        'total_artworks': artworks.count(),
    }
    return render(request, 'accounts/artist_dashboard.html', context)


def register(request):
    error = ""
    if request.method == "POST":
        username = request.POST.get("username", "")
        email = request.POST.get("email", "")
        password = request.POST.get("password", "")
        user_type = request.POST.get("user_type", "buyer")

        if CustomUser.objects.filter(username=username).exists():
            error = "Username already registered."
        else:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                user_type=user_type
            )
            login(request, user)

            # Redirect artists to add artwork page
            if user.user_type == 'artist':
                return redirect('add_artwork')

            return redirect("home")

    return render(request, "accounts/register.html", {"error": error})


def login_view(request):
    error = ""
    if request.method == "POST":
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            error = "Invalid username or password"

    return render(request, "accounts/login.html", {"error": error})


def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def profile(request):
    return render(request, "accounts/profile.html", {"user": request.user})


@login_required
def artists_list(request):
    artists = CustomUser.objects.filter(user_type='artist')
    return render(request, 'accounts/artists_list.html', {'artists': artists})


@login_required
def artist_detail(request, pk):
    artist = get_object_or_404(CustomUser, pk=pk)

    # ✅ SAFE artwork lookup
    artworks = Artwork.objects.filter(artist=artist)

    # ✅ Correct artist-level ratings
    ratings = ArtistRating.objects.filter(artist=artist)
    avg_rating = ratings.aggregate(Avg('rating'))['rating__avg'] or 0

    review_form = ArtistRatingForm()

    if request.method == "POST":
        review_form = ArtistRatingForm(request.POST)
        if review_form.is_valid():
            rating = review_form.save(commit=False)
            rating.artist = artist
            rating.rater = request.user
            rating.save()
            return redirect('artist_detail', pk=pk)

    context = {
        'artist': artist,
        'artworks': artworks,
        'ratings': ratings,
        'avg_rating': avg_rating,
        'review_form': review_form,
    }
    return render(request, "accounts/artist_detail.html", context)
