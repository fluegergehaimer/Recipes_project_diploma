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


def validate_username_via_regex(username):
    """Валидация поля username."""
    if not re.match(USERNAME_VALID_PATTERN, username):
        invalid_characters = re.sub(USERNAME_VALID_PATTERN, '', username)
        raise ValidationError(
            f'В username найдены недопустимые символы:'
            f'{"".join(invalid_characters)}'
        )
    return username
