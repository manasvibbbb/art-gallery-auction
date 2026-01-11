from django import forms
from .models import ArtistRating

class ArtistRatingForm(forms.ModelForm):
    class Meta:
        model = ArtistRating
        fields = ['rating', 'review']
        widgets = {
            'rating': forms.Select(choices=[(i,i) for i in range(1,6)], attrs={'class':'form-control'}),
            'review': forms.Textarea(attrs={'class':'form-control', 'rows':3}),
        }
