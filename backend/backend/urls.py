from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

from recipes.views import get_recipe_by_short_link

urlpatterns = [
    path('admin/', admin.site.urls),
    path('recipes/<int:pk>/', get_recipe_by_short_link, name='recipes-detail'),
    path('api/', include('api.urls')),
    path('s/', include('recipes.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
