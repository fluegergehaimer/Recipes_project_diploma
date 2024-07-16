import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


MODEL_AND_FILE = {
    Ingredient: "ingredients.json",
}


class Command(BaseCommand):
    def import_ingredients(self, data):
        try:
            ingredients = [
                Ingredient(
                    **ingredient
                ) for ingredient in data
            ]
            Ingredient.objects.bulk_create(ingredients)
            print('Ингридиенты добавлены!')
        except Exception as ex:
            print(str(ex))
            print(
                'Произошла ошибка при добавлении '
                'ингредиента.'
            )

    def handle(self, *args, **options):
        for (model, file_name) in MODEL_AND_FILE.items():
            file_path = os.path.join(
                settings.BASE_DIR,
                'data',
                file_name,
            )
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                return self.import_ingredients(data)
