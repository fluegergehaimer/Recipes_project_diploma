from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from recipes.models import Recipe
from api.serializers import DisplayRecipesSerializer


class ShortLinkView(APIView):
    def get(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        return Response(
            DisplayRecipesSerializer(recipe).data,
            status=status.HTTP_200_OK
        )
