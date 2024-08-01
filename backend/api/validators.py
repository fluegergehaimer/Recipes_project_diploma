from rest_framework.exceptions import ValidationError


def check_unique_items(data):
    if not data:
        raise ValidationError('Поле не может быть пустым.')
    unique_items = set(data)
    if len(data) != len(unique_items):
        raise ValidationError(
            f'{unique_items} уже добавлены.'
        )
