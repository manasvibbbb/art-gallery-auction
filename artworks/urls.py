from django.urls import path
from . import views

urlpatterns = [path('', views.artwork_list, name='artwork_list'),
               path('<int:pk>/', views.artwork_detail, name='artwork_detail'),
               path('upload/', views.upload_artwork, name='upload_artwork'),
               path('my-artworks/', views.my_artworks, name='my_artworks'),
               path('ai-studio/', views.ai_studio, name='ai_studio'),
               path('ai-studio/save/', views.save_concept_art, name='save_concept_art'),
               path('add-artwork/', views.add_artwork, name='add_artwork'),
]
