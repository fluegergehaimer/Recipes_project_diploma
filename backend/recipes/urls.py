from django.urls import path
# from .views import ShortLinkView
from api.views import get_recipe_by_short_link

urlpatterns = [
    # path('<int:pk>/', ShortLinkView.as_view(), name='shortlink'),
    path(
        '<int:pk>/',
        get_recipe_by_short_link,
        name='shortlink'
    )
]
