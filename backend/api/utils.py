from datetime import datetime


def generate_shopping_list(recipe_ingredients, recipes):
    shopping_list = "\n".join([
        f'{index}. '
        f'{item["ingredient__name"].capitalize()} - '
        f'{item["amount"]}'
        f'({item["ingredient__measurement_unit"]}).'
        for index, item in enumerate(recipe_ingredients, start=1)
    ])
    recipe_names = '\n'.join(
        recipe for recipe in recipes.values_list('name', flat=True)
    )
    return (
        f'Список покупок от {datetime.now().strftime("%d-%m-%Y %H:%M")}.'
        f'\n\nКупить:\n'
        f'{shopping_list}\n\nДля рецептов:\n{recipe_names}'
    )


def get_ingredients_values(lst, key):
    filtered_list = filter(lambda d: key in d, lst)
    result = [d[key] for d in filtered_list]
    return result
