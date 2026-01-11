import base64
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.shortcuts import render, redirect, get_object_or_404
from auctions.models import Auction
from .ai_service import generate_ai_image
from .forms import AIArtGenerationForm, SaveConceptArtForm, ArtworkForm
from .models import Artwork


def home(request):
    """Homepage - displays featured artworks"""
    artworks = Artwork.objects.all()[:6]
    return render(request, 'home.html', {'artworks': artworks})


@login_required
def artwork_list(request):
    """Display all artworks"""
    artworks = Artwork.objects.all()
    return render(request, 'artworks/artwork_list.html', {'artworks': artworks})


@login_required
def upload_artwork(request):
    """Upload new artwork"""
    if request.method == 'POST':
        form = ArtworkForm(request.POST, request.FILES)
        if form.is_valid():
            artwork = form.save(commit=False)
            artwork.artist = request.user
            artwork.save()
            if artwork.sale_type == 'auction':
                return redirect('auctions:create_auction', artwork_id=artwork.id)
            return redirect('artist_dashboard')
    else:
        form = ArtworkForm()
    return render(request, 'artworks/upload.html', {'form': form})


@login_required
def my_artworks(request):
    """Display user's own artworks"""
    artworks = Artwork.objects.filter(artist=request.user)
    return render(request, 'artworks/my_artworks.html', {'artworks': artworks})


@login_required
def gallery(request):
    """Gallery view"""
    artworks = Artwork.objects.all()
    return render(request, "artworks/home.html", {"artworks": artworks})


@login_required
def artwork_detail(request, pk):
    """Display artwork details"""
    artwork = get_object_or_404(Artwork, pk=pk)

    try:
        auction = Auction.objects.filter(artwork=artwork).first()
    except:
        auction = None

    return render(
        request,
        "artworks/artwork_detail.html",
        {"artwork": artwork, "auction": auction},
    )


@login_required
def artists_list(request):
    """Display list of artists"""
    from accounts.models import CustomUser
    artists = CustomUser.objects.filter(user_type='artist')
    return render(request, 'artworks/artists_list.html', {'artists': artists})


@login_required
def ai_studio(request):
    """AI Art Studio - Generate concept art"""
    form = AIArtGenerationForm()
    context = {
        'form': form,
        'has_preview': False,
    }

    if request.method == 'POST':
        form = AIArtGenerationForm(request.POST)
        if form.is_valid():
            prompt = form.cleaned_data['prompt']
            style = form.cleaned_data['style']
            width = int(form.cleaned_data['width'])

            result = generate_ai_image(prompt, style, width)

            if result['success']:
                request.session['preview_prompt'] = prompt
                request.session['preview_style'] = style
                request.session['preview_image_base64'] = result['image_base64']

                context['has_preview'] = True
                context['preview_prompt'] = prompt
                context['preview_style'] = style
                context['preview_image_url'] = f"data:image/png;base64,{result['image_base64']}"
                context['form'] = form
            else:
                context['error'] = result['error']
                context['form'] = form
        else:
            context['form'] = form

    return render(request, 'artworks/ai_studio.html', context)


@login_required
def save_concept_art(request):
    """Save AI-generated concept art"""
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        image_base64 = request.session.get('preview_image_base64', '')

        if not title:
            return render(request, 'artworks/save_concept_art.html', {
                'error': 'Please provide a title',
            })

        if image_base64:
            try:
                image_data = base64.b64decode(image_base64)
            except Exception as e:
                return render(request, 'artworks/save_concept_art.html', {
                    'error': f'Error processing image: {str(e)}'
                })

            artwork = Artwork.objects.create(
                title=title,
                description=description,
                artist=request.user,
                price=0
            )

            filename = f"ai_generated_{artwork.pk}.png"
            artwork.image.save(filename, ContentFile(image_data), save=True)

            return redirect('artwork_detail', pk=artwork.pk)

        return render(request, 'artworks/save_concept_art.html', {
            'error': 'No image to save. Please generate an image first.'
        })

    image_base64 = request.session.get('preview_image_base64', '')
    image_url = f"data:image/png;base64,{image_base64}" if image_base64 else ''

    return render(request, 'artworks/save_concept_art.html', {
        'preview_image_url': image_url,
        'form': SaveConceptArtForm(),
    })

@login_required
def winners_list(request):
    """Display auction winners"""
    try:
        completed_auctions = Auction.objects.filter(status='completed')
        return render(request, 'artworks/winners_list.html', {'auctions': completed_auctions})
    except:
        return render(request, 'artworks/winners_list.html', {'auctions': []})


@login_required
def add_artwork(request):
    if request.user.user_type != 'artist':
        return redirect('home')

    if request.method == 'POST':
        form = ArtworkForm(request.POST, request.FILES)
        if form.is_valid():
            artwork = form.save(commit=False)
            artwork.artist = request.user
            artwork.save()

            if artwork.sale_type == 'auction':
                return redirect('auctions:create_auction', artwork_id=artwork.id)
            return redirect('artist_dashboard')
    else:
        form = ArtworkForm()

    return render(request, 'artworks/add_artwork.html', {'form': form})
