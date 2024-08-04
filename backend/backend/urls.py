from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

from recipes.views import ShortLinkView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('recipes/<int:id>/', ShortLinkView.as_view(), name='shortlink'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
