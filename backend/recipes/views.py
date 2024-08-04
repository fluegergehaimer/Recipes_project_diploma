from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from rest_framework.decorators import api_view

from .models import Recipe


@api_view(['GET'])
def get_recipe_by_short_link(request, pk=None):
    recipe = get_object_or_404(Recipe, id=pk)
    full_api_url = request.build_absolute_uri(
        reverse(
            'recipes-detail',
            args=[recipe.id]
        )
    )
    return redirect(full_api_url)
