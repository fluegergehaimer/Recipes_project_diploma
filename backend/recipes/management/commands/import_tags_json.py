import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Tag


MODEL_AND_FILE = {
    Tag: "tags.json",
}


class Command(BaseCommand):
    def import_tags(self, data):
        for tag in data:
            try:
                unit, created = Tag.objects.get_or_create(**tag)
                if created:
                    unit.save()
                    display_format = 'Тэг {} добавлен.'
                    print(display_format.format(unit))
            except Exception as ex:
                print(str(ex))
                msg = (
                    'Произошла ошибка при добавлении.'
                )
                print(msg)

    def handle(self, *args, **options):
        for (model, file_name) in MODEL_AND_FILE.items():
            file_path = os.path.join(
                settings.BASE_DIR,
                'data',
                file_name,
            )
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                return self.import_tags(data)
