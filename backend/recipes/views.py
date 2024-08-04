# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from django.shortcuts import redirect
# # get_object_or_404
# from django.urls import reverse

# from recipes.models import Recipe
# # from api.serializers import DisplayRecipesSerializer


# class ShortLinkView(APIView):
#     def get_recipe_by_short_link(self, request, short_link=None):
#         recipe_id = short_link.split('/')[-1]  # Предполагается, что идентификатор находится в конце URL

#         try:
#             recipe = Recipe.objects.get(id=recipe_id)
#         except Recipe.DoesNotExist:
#             return Response({'error': 'Recipe not found'}, status=status.HTTP_404_NOT_FOUND)

#         detail_url = reverse('custom-recipes-detail', kwargs={'pk': recipe.id})

#         full_api_url = request.build_absolute_uri(detail_url)

        
#         return redirect('custom-recipes-detail', kwargs={'pk': recipe.id})

#         # return Response({'full_api_url': full_api_url}, status=status.HTTP_200_OK)
    #     )
