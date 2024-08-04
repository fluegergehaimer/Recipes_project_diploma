from django.urls import path
from api.views import get_recipe_by_short_link

urlpatterns = [
    path(
        '<int:pk>/',
        get_recipe_by_short_link,
        name='shortlink'
    )
]
