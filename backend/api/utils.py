from datetime import datetime

from django.db.models import Sum
from rest_framework.exceptions import ValidationError
import pymorphy2

from recipes.models import ShoppingCart


morph = pymorphy2.MorphAnalyzer()


def generate_shopping_list(request):
    ingredients = ShoppingCart.objects.filter(
        user=request.user
    ).values(
        'recipe__ingredients__name',
        'recipe__ingredients__measurement_unit',
        'recipe__name'
    ).annotate(
        total_quantity=Sum('recipe__recipe_ingredients__amount')
    )
    shopping_list = ([
        f'{index + 1}. '
        f'{item["recipe__ingredients__name"].capitalize()} - '
        f'{item["total_quantity"]} '
        f'{item["recipe__ingredients__measurement_unit"]}.'
        for index, item in enumerate(ingredients)
    ])
    recipes = list(set([
        f'{name["recipe__name"]} '
        for name in ingredients
    ]))
    return (
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


def morph_parse(word, num):
    return morph.parse(word)[0].make_agree_with_number(num).word
