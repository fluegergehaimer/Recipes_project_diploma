from datetime import datetime

from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_short_url.views import get_surl
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.permissions import (
    AllowAny, IsAuthenticated,
    IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response

from recipes.models import (
    Favorite, Ingredient,
    Recipe, ShoppingCart,
    Subscription, Tag, FoodgramUser
)
from .filters import IngredientFilter, RecipeFilter
from .paginators import PageLimitPaginator, SubscriptionPaginator
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    AvatarSerializer, FoodgramUserSerializer, FavoriteSerializer,
    IngredientSerializer, RecipeGetSerializer, RecipeSerializer,
    ShoppingCartSerializer, SubscriptionCreateSerializer,
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
            serializers = AvatarSerializer(user, data=request.data)
            serializers.is_valid(raise_exception=True)
            serializers.save()
            return Response(serializers.data, status=200)
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
    def add_recipe_to_collection(request, pk, serialiser, model):
        if request.method == 'POST':
            user = request.user.id
            serializer_create = serialiser(
                data={
                    'user': user,
                    'recipe': pk,
                }
            )
            serializer_create.is_valid(raise_exception=True)
            serializer_create.save()
            return Response(
                serializer_create.data, status=status.HTTP_201_CREATED
            )
        get_object_or_404(model, recipe=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, pk):
        return self.add_recipe_to_collection(
            request,
            pk,
            FavoriteSerializer,
            Favorite
        )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, pk):
        return self.add_recipe_to_collection(
            request,
            pk,
            ShoppingCartSerializer,
            ShoppingCart
        )

    @action(
        detail=False, methods=['get'], permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        return FileResponse(
            generate_shopping_list(request),
            as_attachment=True,
            content_type='txt',
            filename=f'{datetime.now()}_shopping_list.txt'
        )

    @action(
        methods=['get'],
        detail=True,
        url_path='get-link',
        url_name='get-link',
    )
    def get_link(self, request, pk=None):
        long_url = request.path
        short_url = request.META.get(
            'HTTP_HOST'
        ) + f'/recipes/{id}' + get_surl(long_url)
        response = Response(
            {'short-link': short_url},
            status=status.HTTP_200_OK
        )
        return response


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    permission_classes = (AllowAny, )
    serializer_class = TagSerializer
    pagination_class = None


class SubscriptionListView(ListAPIView):
    serializer_class = SubscriptionCreateSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_pagination_class(self):
        if self.action in ['create', 'list']:
            return SubscriptionPaginator
        return PageLimitPaginator

    def get_queryset(self):
        limit = int(self.request.GET.get('limit', 10**10))
        return self.request.user.subscribers.all().order_by(
            'subscribed_to__username'
        )[:limit]
