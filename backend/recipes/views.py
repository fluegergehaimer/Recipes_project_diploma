from rest_framework.views import APIView
from .models import Recipe


class ShortLinkView(APIView):
    model = Recipe
