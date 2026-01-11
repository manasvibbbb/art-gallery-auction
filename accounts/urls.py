from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile, name="profile"),
    path("artists/", views.artists_list, name="artists_list"),
    path("artists/<int:pk>/", views.artist_detail, name="artist_detail"),
    path('artist-dashboard/', views.artist_dashboard, name='artist_dashboard'),

]
