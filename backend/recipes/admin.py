from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.utils.safestring import mark_safe

from .models import (
    Favorite, Tag, Ingredient, Recipe,
    RecipeIngredient, ShoppingCart, Subscription, FoodgramUser
)


admin.site.unregister(Group)


class IngredientInline(admin.TabularInline):
    model = RecipeIngredient


class CookingTimeFilter(admin.SimpleListFilter):
    title = ('Время приготовления')
    parameter_name = 'cooking_time'

    def lookups(self, request, model_admin):
        return [
            ('fast', ('быстрые, до 15мин.')),
            ('medium', ('средние, до 30мин.')),
            ('long', ('долгие, 30мин. и более')),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'fast':
            return queryset.filter(cooking_time__range=(0, 15))
        if self.value() == 'medium':
            return queryset.filter(cooking_time__range=(15, 30))
        if self.value() == 'long':
            return queryset.filter(cooking_time__range=(30, 10**10))
        return queryset


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
    )
    search_fields = (
        'name',
        'slug',
    )


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',
        'get_recipes'
    )
    list_filter = (
        'measurement_unit',
    )
    search_fields = (
        'name',
        'measurement_unit'
    )

    @admin.display(description='рецепты')
    def get_recipes(self, ingredient):
        return ingredient.recipes.count()


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = [IngredientInline]

    list_display = (
        'name',
        'author',
        'get_tags',
        'cooking_time',
        'get_ingredients',
        'image_preview',
        'favorites_count',
    )
    search_fields = (
        'name',
        'tags'
    )
    list_filter = (
        'author',
        'tags',
        CookingTimeFilter
    )

    @admin.display(description='Тэги')
    def get_tags(self, recipe):
        return mark_safe('<br> '.join(
            recipe.tags.all().values_list('name', flat=True)
        ))

    @admin.display(description='Продукты')
    def get_ingredients(self, recipe):
        return mark_safe('<br> '.join([
            f'{ingredient.ingredient.name} - '
            f'{ingredient.amount} '
            f'({ingredient.ingredient.measurement_unit})'
            for ingredient in recipe.recipe_ingredients.all()])
        )

    @admin.display(description='В избранном')
    def favorites_count(self, recipes):
        return recipes.favorites.count()

    @admin.display(
        description=('image'),
    )
    def image_preview(self, url):
        return mark_safe(
            f'<img src="{url.image.url}" width=40 height=40 />'
        )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'subscribed_to',
        'subscriber'
    )


@admin.register(FoodgramUser)
class FoodgramUserAdmin(UserAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'get_recipes_count',
        'get_subscribers',
        'get_subscriptions'
    )
    search_fields = (
        'email',
        'username'
    )
    list_filter = (
        'is_staff',
        'is_active'
    )

    @admin.display(description='Рецепты')
    def get_recipes_count(self, user):
        return user.recipes.count()

    @admin.display(description='Подписчики')
    def get_subscribers(self, user):
        return user.subscribers.count()

    @admin.display(description='Подписки')
    def get_subscriptions(self, user):
        return user.authors.count()


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = (
        'ingredient',
        'recipe',
        'amount'
    )


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe'
    )


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe'
    )
