from datetime import datetime


def generate_shopping_list(ingredients):
    # shopping_list = [
    #     f'{index}. '
    #     f'{item["ingredient__name"].capitalize()} - '
    #     f'{item["total_quantity"]} '
    #     f'{item["ingredient__measurement_unit"]}.'
    #     for index, item in enumerate(ingredients, start=1)
    # ]
    products = {}
    for item in ingredients:
        name = item['ingredient__name']
        unit = item['ingredient__measurement_unit']
        amount = item['total_quantity']
        if name in products:
            products[name]['amount'] += item['total_quantity']
        products[name] = {
            'unit': unit,
            'amount': amount,
        }
    shopping_list = [
        f'{name.capitalize()} - '
        f'{item["amount"]} '
        f'({item["unit"]}).'
        for name, item in products.items()
    ]
    recipes = list(set([
        f'{name["recipe__name"]} '
        for name in ingredients
    ]))
    return (
        f'Список покупок {datetime.now()}.\nПродукты:\n'
        f'{shopping_list}\nДля рецептов:\n{recipes}'
    )


def get_ingredients_values(lst, key):
    filtered_list = filter(lambda d: key in d, lst)
    result = [d[key] for d in filtered_list]
    return result
