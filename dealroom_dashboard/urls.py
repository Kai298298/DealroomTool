"""
URL-Konfiguration für das Dealroom Dashboard
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.urls import re_path
import os

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Core-App
    path('', include('core.urls')),
    
    # Users-App
    path('users/', include('users.urls')),
    
    # Dealrooms-App
    path('dealrooms/', include('deals.urls')),
    
    # Files-App
    path('files/', include('files.urls')),
    
    # Generierte Webseiten
    re_path(r'^generated_pages/(?P<path>.*)$', serve, {
        'document_root': os.path.join(settings.BASE_DIR, 'generated_pages'),
    }),
]

# Media-Dateien im Development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Admin-Site-Konfiguration
admin.site.site_header = "Dealroom Dashboard Administration"
admin.site.site_title = "Dealroom Dashboard"
admin.site.index_title = "Willkommen im Dealroom Dashboard"

# URL-Patterns für generierte Websites
urlpatterns += [
    # Generierte Websites hosten
    re_path(
        r'^generated_pages/dealroom-(?P<dealroom_id>\d+)/(?P<path>.*)$',
        serve,
        {
            'document_root': os.path.join(settings.BASE_DIR, 'generated_pages'),
            'show_indexes': False,
        },
        name='generated_website'
    ),
]
