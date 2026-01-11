from django import forms
from .models import Artwork


class AIArtGenerationForm(forms.Form):
    """Form for users to generate AI images"""

    STYLE_CHOICES = [
        ('realistic', 'Realistic'),
        ('oil_painting', 'Oil Painting'),
        ('digital_art', 'Digital Art'),
        ('watercolor', 'Watercolor'),
        ('anime', 'Anime Style'),
        ('cartoon', 'Cartoon'),
        ('sketch', 'Pencil Sketch'),
        ('cyberpunk', 'Cyberpunk'),
        ('fantasy', 'Fantasy'),
    ]

    prompt = forms.CharField(
        label='Describe your artwork concept',
        widget=forms.Textarea(attrs={
            'placeholder': 'E.g., "A serene mountain landscape with golden sunset and misty valleys"',
            'rows': 4,
            'class': 'form-control',
            'style': 'font-family: inherit; resize: vertical;',
        }),
        max_length=1000,
        help_text='Be specific for better results (colors, style, mood, lighting)',
        required=True,
    )

    style = forms.ChoiceField(
        label='Art Style',
        choices=STYLE_CHOICES,
        initial='realistic',
        widget=forms.Select(attrs={
            'class': 'form-control',
        }),
    )

    width = forms.ChoiceField(
        label='Width (pixels)',
        choices=[
            ('512', '512px (fast)'),
            ('768', '768px (balanced)'),
            ('1024', '1024px (high quality, slower)'),
        ],
        initial='512',
        widget=forms.Select(attrs={
            'class': 'form-control',
        }),
    )


class SaveConceptArtForm(forms.ModelForm):
    """Form to save generated image as concept artwork"""

    class Meta:
        model = Artwork
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'E.g., "Mountain Sunset Concept #1"',
                'class': 'form-control',
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'Add notes, tags, or refinement ideas...',
                'rows': 3,
                'class': 'form-control',
            }),
        }
        labels = {
            'title': 'Artwork Title',
            'description': 'Description (optional)',
        }
class ArtworkForm(forms.ModelForm):
    class Meta:
        model = Artwork
        fields = ['title', 'description', 'image', 'price', 'sale_type']
        widgets = {
            'sale_type': forms.RadioSelect(choices=Artwork.SALE_TYPES),
            'description': forms.Textarea(attrs={'rows': 4}),
        }