from django_filters.rest_framework import FilterSet, filters

from recipes.models import Ingredient, Recipe


class RecipeFilter(FilterSet):
    author = filters.CharFilter()
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug', lookup_expr='contains'
    )
    is_favorited = filters.BooleanFilter(
        field_name='is_favorited',
        method='filter_is_favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        field_name='is_in_shopping_cart',
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_favorited', 'is_in_shopping_cart']

    def filter_is_favorited(self, recipes, name, value):
        if self.request.user.is_authenticated and value:
            return recipes.filter(favorites__user=self.request.user)
        return recipes

    def filter_is_in_shopping_cart(self, recipes, name, value):
        if self.request.user.is_authenticated and value:
            return recipes.filter(shoppingcarts__user=self.request.user)
        return recipes


class IngredientFilter(FilterSet):
    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name', )
