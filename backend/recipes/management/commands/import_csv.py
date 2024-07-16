"""Команда для импорта csv-файлов."""
import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient, Tag


csv_files = [
    'ingredients.csv',
    'tags.csv',
]

csv_fields = {
    'ingredients.csv': ['name', 'measurement_unit'],
    'tags.csv': ['name', 'color', 'slug'],
}

Models = {
    'ingredients': Ingredient,
    'tags': Tag,
}


def csv_reader_file(csv_file_name):
    """Функция чтения из файла."""
    file_path = os.path.join(
        settings.BASE_DIR,
        'data',
        csv_file_name,
    )
    with open(
        file_path,
        'r',
        encoding='utf-8'
    )as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)
        return list(csvreader)


class Command(BaseCommand):
    """Класс команды."""

    def handle(self, *args, **options):
        """Функция валидации полей и импорта."""
        for csv_file_name in csv_files:
            for row in csv_reader_file(csv_file_name):
                model = csv_file_name.split('.')[0]
                model_class = Models.get(model)
                item = None
                if model_class == Ingredient:
                    item = Ingredient(
                        name=row[0],
                        measurement_unit=row[1]
                    )
                elif model_class == Tag:
                    item = Tag(
                        name=row[0],
                        color=row[1],
                        slug=row[2]
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            f'Не удалось создать запись {model}'
                        )
                    )
                    continue
                item.full_clean()
                item.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Запись для модели {model} добавлена: {row}'
                    )
                )
