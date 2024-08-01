from datetime import datetime

from django.db import IntegrityError
from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import baseconv
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView
from rest_framework.permissions import (
    AllowAny, IsAuthenticated,
    IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response
from rest_framework.views import APIView

from recipes.models import (
    Favorite, Ingredient,
    Recipe, RecipeIngredient, ShoppingCart,
    Subscription, Tag, FoodgramUser
)
from .filters import IngredientFilter, RecipeFilter
from .paginators import PageLimitPaginator
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    AvatarSerializer, DisplayRecipesSerializer,
    FoodgramUserSerializer, IngredientSerializer, RecipeGetSerializer,
    RecipeSerializer,
    SubscriptionCreateSerializer,
    TagSerializer,
)
from .utils import generate_shopping_list


class FoodgramUserViewSet(UserViewSet):
    queryset = FoodgramUser.objects.all()
    serializer_class = FoodgramUserSerializer
    pagination_class = PageLimitPaginator
    http_method_names = ('get', 'post', 'put', 'delete')

    def get_permissions(self):
        if self.action == 'me':
            return [IsAuthenticated()]
        return super().get_permissions()

    @action(detail=True, methods=['post', 'delete'])
    def subscribe(self, request, id):
        if request.method == 'POST':
            subscribed_to = get_object_or_404(FoodgramUser, pk=id)
            subscriber = request.user

            serializer_create = SubscriptionCreateSerializer(
                data={
                    'subscribed_to': subscribed_to.id,
                    'subscriber': subscriber.id,
                },
                context={'request': request}
            )
            serializer_create.is_valid(raise_exception=True)
            serializer_create.save()
            return Response(
                serializer_create.data, status=status.HTTP_201_CREATED
            )
        get_object_or_404(Subscription, subscribed_to=id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['put', 'delete'], detail=True)
    def avatar(self, request, **kwargs):
        user = get_object_or_404(FoodgramUser, username=request.user)
        if request.method == 'PUT':
            serializer = AvatarSerializer(user, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=200)
        user.avatar = None
        user.save()
        return Response(status=204)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        IsAuthorOrReadOnly)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    search_fields = ('tags',)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeGetSerializer
        return RecipeSerializer

    @staticmethod
    def add_or_delete_recipe_from_collection(request, pk, model):
        if request.method == 'POST':
            user = request.user
            recipe = get_object_or_404(Recipe, id=pk)
            try:
                model.objects.create(user=user, recipe=recipe)
            except IntegrityError:
                raise ValidationError('Рецепт уже добавлен.')
            return Response(
                DisplayRecipesSerializer(recipe).data,
                status=status.HTTP_201_CREATED
            )
        get_object_or_404(model, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, pk):
        return self.add_or_delete_recipe_from_collection(
            request,
            pk,
            Favorite
        )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, pk):
        return self.add_or_delete_recipe_from_collection(
            request,
            pk,
            ShoppingCart
        )

    @action(
        detail=False, methods=['get'], permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        recipe_ingredients = RecipeIngredient.objects.filter(
            recipe__shoppingcarts__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit',
            'recipe__name'
        ).annotate(
            total_quantity=Sum('amount')
        )
        recipes = [
            f'{recipe["recipe__name"]} '
            for recipe
            in RecipeIngredient.objects.filter(
                recipe__shoppingcarts__user=request.user
            ).values('recipe__name')
        ]

        return FileResponse(
            generate_shopping_list(recipe_ingredients, recipes),
            as_attachment=True,
            content_type='txt',
            filename=f'{datetime.now()}_shopping_list.txt'
        )

    @action(
        methods=['get'],
        detail=True,
        url_path='get-link',
        url_name='get_link',
    )
    def get_link(self, request, pk):
        recipe = self.get_object()
        encode_id = baseconv.base64.encode(recipe.id)
        short_link = request.build_absolute_uri(
            reverse('shortlink', kwargs={'encoded_id': encode_id})
        )
        return Response({'short-link': short_link}, status=status.HTTP_200_OK)


class ShortLinkView(APIView):

    def get(self, request, encoded_id):
        recipe_id = baseconv.base64.decode(encoded_id)
        return redirect(f'recipes/{recipe_id}/',)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    permission_classes = (AllowAny, )
    serializer_class = TagSerializer
    pagination_class = None


class SubscriptionListView(ListAPIView):
    serializer_class = SubscriptionCreateSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = PageLimitPaginator

    def get_queryset(self):
        return self.request.user.subscribers.all()
