from django.urls import path
from api.views import RecipeViewSet

urlpatterns = [
    # path('<int:pk>/', ShortLinkView.as_view(), name='shortlink'),
    path(
        '<int:pk>/',
        RecipeViewSet.as_view({'get': 'get_recipe_by_short_link'}),
        name='shortlink'
    )
]
