# roorkee360/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('news.urls')),  # ✅ Ya 'news/' - confirm karo
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
    
    # Media files serve karne ke liye
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)