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


# def morph_validator():
#     morph = pymorphy2.MorphAnalyzer()
#     morph.parse('ingredient.measurement_unit')[0].make_agree_with_number('recipe_ingredients.amount').word
# def measurement_unit_check():
#     if Ingredient.measurement_unit == 'банка':
#         if recipe.ingredient.amount == 1 or str(recipe.ingredient.amount)[-1] == '1':
#             ingredient.measurement_unit = 'банка'
#         elif recipe.ingredient.amount in [2, 3, 4] or str(recipe.ingredient.amount)[-1] in ['2', '3', '4']:
#             ingredient.measurement_unit = 'банки'
#         else:
#             ingredient.measurement_unit = 'банок'

# 'банка' 'банки' 'банок'  
# батон
# веточка
# г
# горсть
# капля
# кусок
# мл
# ст. л.
# стакан
# ч. л.
# шт.
# щепотка
