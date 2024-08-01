"""Модуль с функциями-валидации."""
import re

from django.core.exceptions import ValidationError
from django.conf import settings
from recipes.constants import USERNAME_VALID_PATTERN


def validate_username(username):
    if username == settings.URL_PROFILE_PREF:
        raise ValidationError(
            f'Использовать имя "{settings.URL_PROFILE_PREF}" в '
            f'качестве username запрещено.'
        )
    return username


def validate_username_symbols(username):
    """Валидация поля username."""
    invalid_characters = re.findall(USERNAME_VALID_PATTERN, username)
    if invalid_characters:
        raise ValidationError(
            f'В username найдены недопустимые символы:'
            f'{"".join(set(invalid_characters))}'
        )
    return username
