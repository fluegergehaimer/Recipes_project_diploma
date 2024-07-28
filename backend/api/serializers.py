from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from recipes.models import (
    Favorite, Ingredient, RecipeIngredient, Recipe,
    ShoppingCart, Subscription, Tag, FoodgramUser
)
from .utils import check_unique_items, get_ingredients_values


class FoodgramUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField()

    class Meta(UserSerializer.Meta):
        model = FoodgramUser
        fields = (
            *UserSerializer.Meta.fields,
            'is_subscribed',
            'avatar',
        )

    def get_is_subscribed(self, user):
        request = self.context['request']
        return (
            request.user.is_authenticated
            and request.user.authors.filter(
                subscriber=user
            ).exists()
        )


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField()

    class Meta:
        model = FoodgramUser
        fields = ('avatar',)


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeIngredientWriteSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeGetSerializer(serializers.ModelSerializer):
    author = FoodgramUserSerializer(many=False, read_only=True)
    ingredients = RecipeIngredientReadSerializer(
        many=True, source='recipe_ingredients'
    )
    tags = TagSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'name', 'text',
            'cooking_time', 'image', 'is_favorited', 'is_in_shopping_cart'
        )
        read_only_fields = ('__all__',)

    def get_is_favorited(self, recipe):
        request = self.context['request']
        return (
            request
            and request.user.is_authenticated
            and Favorite.objects.filter(
                user=request.user,
                recipe=recipe.id
            ).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context['request']
        return (
            request
            and request.user.is_authenticated
            and ShoppingCart.objects.filter(
                user=request.user, recipe=obj.id
            ).exists()
        )


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    author = FoodgramUserSerializer(many=False, read_only=True)
    ingredients = RecipeIngredientWriteSerializer(
        many=True, source='recipe_ingredients'
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )

    class Meta:
        model = Recipe
        fields = fields = (
            'id',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
            'author'
        )

    def to_representation(self, instance):
        return RecipeGetSerializer(
            instance,
            context=self.context
        ).data

    def validate(self, data):
        check_unique_items(data['tags'])
        check_unique_items(
            get_ingredients_values(
                data['recipe_ingredients'], 'id'
            )
        )
        return data

    def validate_image(self, image):
        if not image:
            raise serializers.ValidationError('Это поле не может быть пустым')
        return image

    def create_ingredients(self, ingredients_data, recipe):
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount'],
            ) for ingredient in ingredients_data
        )

    def create(self, validated_data):
        ingredients_data = validated_data.pop('recipe_ingredients')
        tags_data = validated_data.pop('tags')
        validated_data['author'] = self.context['request'].user
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)
        self.create_ingredients(ingredients_data, recipe)

        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('recipe_ingredients')
        instance.ingredients.clear()
        tags = validated_data.pop('tags')
        instance.tags.clear()
        instance.tags.set(tags)
        self.create_ingredients(ingredients, recipe=instance)
        instance.save()
        return instance


class DisplayRecipesSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        read_only=True
    )

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionCreateSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source='subscribed_to.recipes.count',
        read_only=True
    )

    class Meta:
        model = Subscription
        fields = ('subscribed_to', 'subscriber', 'recipes', 'recipes_count')

    def validate(self, data):
        request = self.context['request']
        subscribed_to = data.get('subscribed_to')
        if request.user.id == subscribed_to.id:
            raise ValidationError('Нельзя подписаться на самого себя.')
        if Subscription.objects.filter(
            subscribed_to=subscribed_to.id,
            subscriber=request.user
        ).exists():
            raise ValidationError('Подписка уже существует.')
        return data

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        additional_values = FoodgramUserSerializer(
            instance.subscribed_to,
            context={'request': self.context.get('request')}
        ).data

        for key, value in additional_values.items():
            representation[key] = value

        del representation['subscriber']
        del representation['subscribed_to']

        return representation

    def get_recipes(self, author):
        request = self.context.get('request')
        recipes = author.subscribed_to.recipes.all()
        recipes_limit = int(request.GET.get('recipes_limit', 10**10))
        return DisplayRecipesSerializer(
            recipes[:recipes_limit], many=True
        ).data


class AddToCollectionSerializer(serializers.ModelSerializer):
    def validate(self, data):
        user = data.get('user')
        recipe = data.get('recipe')
        if self.Meta.model.objects.filter(user=user, recipe=recipe).exists():
            raise ValidationError('Рецепт уже добавлен.')
        return data

    def to_representation(self, instance):
        return DisplayRecipesSerializer(
            instance=instance.recipe,
            context={'request': self.context.get('request')}
        ).data


class FavoriteSerializer(AddToCollectionSerializer):
    class Meta:
        model = Favorite
        fields = ('user', 'recipe')


class ShoppingCartSerializer(AddToCollectionSerializer):
    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')
