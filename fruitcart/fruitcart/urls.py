"""
URL configuration for fruitcart project.

In development (DEBUG=True), Django serves uploaded media files directly.
In production, a web server (Nginx/Apache) should serve /media/ instead.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('store.urls')),       # Store: /, /fruits/, /cart/ …
    path('', include('accounts.urls')),    # Auth:  /register/, /login/, /logout/
]

# Serve uploaded media files during development only
# This appends URL patterns like /media/fruits/apple.jpg → MEDIA_ROOT/fruits/apple.jpg
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'store.views.custom_404'
