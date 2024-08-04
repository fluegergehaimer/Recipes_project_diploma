from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import (
    FoodgramUserViewSet, IngredientViewSet, RecipeViewSet,
    TagViewSet, get_recipe_by_short_link
)
# from recipes.views import ShortLinkView

app_name = 'api'

router = DefaultRouter()

router.register('users', FoodgramUserViewSet, basename='users')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('tags', TagViewSet, basename='tags')

urlpatterns = [
    # path('recipe-detail/<int:pk>/', RecipeViewSet.as_view({'get': 'id'}), name='recipe-detail'),
    
    # path('recipe-detail/<int:pk>/', get_recipe_by_short_link, name='recipe-detail'),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
