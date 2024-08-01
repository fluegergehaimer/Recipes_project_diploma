from datetime import datetime


def generate_shopping_list(recipe_ingredients, recipes):
    ingredients = {}
    for item in recipe_ingredients:
        name = item['ingredient__name']
        unit = item['ingredient__measurement_unit']
        amount = item['total_quantity']
        ingredients[name] = {
            'unit': unit,
            'amount': amount,
        }
    shopping_list = "\n".join([
        f'- {name.capitalize()} - '
        f'{item["amount"]}'
        f'({item["unit"]}).'
        for name, item in ingredients.items()
    ])
    return (
        f'Список покупок {datetime.now().strftime("%d-%m-%Y %H:%M")}.'
        f'\nПродукты:\n'
        f'{shopping_list}\nДля рецептов:\n{list(set(recipes))}'
    )


def get_ingredients_values(lst, key):
    filtered_list = filter(lambda d: key in d, lst)
    result = [d[key] for d in filtered_list]
    return result
