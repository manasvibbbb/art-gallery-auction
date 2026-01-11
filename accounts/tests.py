from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import CustomUser


class ArtistDetailViewTests(TestCase):

    def setUp(self):
        """Create a test artist"""
        self.artist = CustomUser.objects.create_user(
            username='testartist',
            email='artist@test.com',
            password='testpass123'
        )
        self.client = Client()

    def test_artist_detail_view_status_code(self):
        """Test if artist detail page returns 200 OK"""
        response = self.client.get(
            reverse('artist_detail', kwargs={'pk': self.artist.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_artist_detail_view_context(self):
        """Test if context contains required variables"""
        response = self.client.get(
            reverse('artist_detail', kwargs={'pk': self.artist.pk})
        )
        self.assertIn('artist', response.context)
        self.assertIn('artworks', response.context)
        self.assertIn('ratings', response.context)
        self.assertIn('avg_rating', response.context)

    def test_artist_detail_correct_template(self):
        """Test if correct template is used"""
        response = self.client.get(
            reverse('artist_detail', kwargs={'pk': self.artist.pk})
        )
        self.assertTemplateUsed(response, 'accounts/artist_detail.html')

    def test_artist_detail_requires_login(self):
        """Test if view requires authentication"""
        response = self.client.get(
            reverse('artist_detail', kwargs={'pk': self.artist.pk})
        )
        self.assertEqual(response.status_code, 302)  # Redirect to login




# Create your tests here.
