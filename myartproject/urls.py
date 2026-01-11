from django.contrib import admin
from django.urls import path, include
from artworks import views as artworks_views
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = "Art Gallery & Auction System"
admin.site.site_title = "Admin Portal"
admin.site.index_title = "Welcome to Art Gallery Admin"

urlpatterns = [
    path('', artworks_views.home, name='home'),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('artworks/', include('artworks.urls')),
    path('auctions/', include('auctions.urls')),
    path('payments/', include('payments.urls')),
    path('accounts/', include('accounts.urls')),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
