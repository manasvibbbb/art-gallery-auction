import base64

from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.shortcuts import render, redirect, get_object_or_404

from .ai_service import generate_ai_image
from .forms import AIArtGenerationForm, SaveConceptArtForm
from .models import Artwork


def home(request):
    """Home page - display featured artworks"""
    artworks = Artwork.objects.all()[:5]
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
        title = request.POST.get('title', '')
        description = request.POST.get('description', '')
        sale_type = request.POST.get('sale_type', 'fixed')
        image = request.FILES.get('image')

        if sale_type == 'fixed':
            fixed_price = request.POST.get('fixed_price', 0)
            artwork = Artwork.objects.create(
                artist=request.user,
                title=title,
                description=description,
                image=image,
                sale_type=sale_type,
                fixed_price=fixed_price,
            )
        else:
            starting_price = request.POST.get('starting_price', 0)
            artwork = Artwork.objects.create(
                artist=request.user,
                title=title,
                description=description,
                image=image,
                sale_type=sale_type,
                starting_price=starting_price,
            )

        return redirect('artwork_detail', pk=artwork.pk)

    return render(request, 'artworks/upload.html')


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

    # Try to get auction if it exists (from auctions app)
    try:
        from auctions.models import Auction
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
    from django.contrib.auth.models import User
    artists = User.objects.filter(artwork__isnull=False).distinct()
    return render(request, 'artworks/artists_list.html', {'artists': artists})


# ============ AI STUDIO VIEWS ============

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

            # Call AI service to generate image
            result = generate_ai_image(prompt, style, width)

            if result['success']:
                # Store in session for save later
                request.session['preview_prompt'] = prompt
                request.session['preview_style'] = style
                request.session['preview_image_base64'] = result['image_base64']

                context['has_preview'] = True
                context['preview_prompt'] = prompt
                context['preview_style'] = style
                context['preview_image_url'] = f"data:image/png;base64,{result['image_base64']}"
                context['form'] = form
            else:
                # Show error
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
        prompt = request.session.get('preview_prompt', '')
        image_base64 = request.session.get('preview_image_base64', '')
        style = request.session.get('preview_style', '')

        if not title:
            prompt = request.session.get('preview_prompt', '')
            image_url = f"data:image/png;base64,{request.session.get('preview_image_base64', '')}" if request.session.get(
                'preview_image_base64') else ''

            return render(request, 'artworks/save_concept_art.html', {
                'error': 'Please provide a title',
                'preview_prompt': prompt,
                'preview_image_url': image_url,
            })

        # Save base64 image to file
        if image_base64:
            # Decode base64
            try:
                image_data = base64.b64decode(image_base64)
            except Exception as e:
                return render(request, 'artworks/save_concept_art.html', {
                    'error': f'Error processing image: {str(e)}'
                })

            # Create artwork
            artwork = Artwork.objects.create(
                title=title,
                description=description,
                artist=request.user,
                is_ai_generated=True,
                prompt=prompt,
                source_model='Stability AI'
            )

            # Save image
            filename = f"ai_generated_{artwork.pk}.png"
            artwork.image.save(filename, ContentFile(image_data), save=True)

            return redirect('artwork_detail', pk=artwork.pk)

        # No image in session
        return render(request, 'artworks/save_concept_art.html', {
            'error': 'No image to save. Please generate an image first.'
        })

    # GET request - show save form with preview
    prompt = request.session.get('preview_prompt', '')
    image_base64 = request.session.get('preview_image_base64', '')
    image_url = f"data:image/png;base64,{image_base64}" if image_base64 else ''

    return render(request, 'artworks/save_concept_art.html', {
        'preview_prompt': prompt,
        'preview_image_url': image_url,
        'form': SaveConceptArtForm(),
    })


@login_required
def winners_list(request):
    """Display auction winners"""
    try:
        from auctions.models import Auction
        completed_auctions = Auction.objects.filter(status='completed')
        return render(request, 'artworks/winners_list.html', {'auctions': completed_auctions})
    except:
        # If auctions app doesn't exist, show empty list
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

            # Redirect based on sale type
            if artwork.sale_type == 'auction':
                return redirect('auctions:create_auction', artwork_id=artwork.id)
            return redirect('artist_dashboard')
    else:
        form = ArtworkForm()

    return render(request, 'artworks/add_artwork.html', {'form': form})


@login_required
def artist_dashboard(request):
    if request.user.user_type != 'artist':
        return redirect('home')

    artworks = Artwork.objects.filter(artist=request.user)
    has_artworks = artworks.exists()

    return render(request, 'accounts/artist_dashboard.html', {
        'artworks': artworks,
        'has_artworks': has_artworks,
    })