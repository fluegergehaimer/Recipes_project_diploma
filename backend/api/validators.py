from rest_framework.exceptions import ValidationError


def check_items(data):
    if not data:
        raise ValidationError('Поле не может быть пустым.')
    unique_items = set(data)
    if len(data) != len(unique_items):
        items = [item for item in data if item in unique_items]
        raise ValidationError(
            f'{items} не должны повторяться.'
        )
