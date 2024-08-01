from rest_framework.exceptions import ValidationError


def check_items(data):
    if not data:
        raise ValidationError('Поле не может быть пустым.')
    unique_items = set(data)
    if len(data) != len(unique_items):
        items = [item for item in unique_items if item in data]
        raise ValidationError(
            f'{items} уже добавлены.'
        )
