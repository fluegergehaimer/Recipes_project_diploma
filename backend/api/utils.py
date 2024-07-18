from datetime import datetime

from django.db.models import Sum
from rest_framework.exceptions import ValidationError

from recipes.models import RecipeIngredient


def generate_shopping_list(request):
    ingredients = RecipeIngredient.objects.filter(
        recipe__shoppingcarts__user=request.user
    ).values(
        'ingredient__name', 'ingredient__measurement_unit', 'recipe__name'
    ).annotate(
        total_quantity=Sum('amount')
    )
    shopping_list = [
        f'{index + 1}. '
        f'{item["ingredient__name"].capitalize()} - '
        f'{item["total_quantity"]} '
        f'{item["ingredient__measurement_unit"]}.'
        for index, item in enumerate(ingredients)
    ]
    recipes = list(*set(
        RecipeIngredient.objects.filter(
            recipe__shoppingcarts__user=request.user
        ).values_list('recipe__name')
    ))
    return ''.join(
        f'Список покупок {datetime.now()}.\nПродукты:\n'
        f'{shopping_list}\nДля рецептов:\n{recipes}'
    )


def check_unique_items(data):
    if not data:
        raise ValidationError('Поле не может быть пустым.')
    unique_items = set(data)
    if len(data) != len(unique_items):
        raise ValidationError(
            f'{unique_items} уже добавлены.'
        )


def get_ingredients_values(lst, key):
    filtered_list = filter(lambda d: key in d, lst)
    result = [d[key] for d in filtered_list]
    return result
