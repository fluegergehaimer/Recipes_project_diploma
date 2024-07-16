from colorfield.fields import ColorField
from django.contrib.auth.models import AbstractUser
from django.core.validators import (
    RegexValidator, MinValueValidator
)
from django.db import models

from .constants import (
    COLOR_MAX_LENGTH, EMAIL_MAX_LENGTH, MAX_LENGTH,
    MIN_VALUE, TEXT_LIMIT, USER_MAX_LENGTH
)
from .validators import (validate_username, validate_username_via_regex)


MIN_MESSAGE = 'Значение не может быть меньше {MIN_VALUE}'


class FoodgramUser(AbstractUser):
    """Модель пользователя."""
    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=USER_MAX_LENGTH,
        unique=True,
        validators=[validate_username, validate_username_via_regex]
    )
    password = models.CharField(
        max_length=USER_MAX_LENGTH,
        verbose_name='Пароль'
    )
    email = models.EmailField(
        max_length=EMAIL_MAX_LENGTH,
        verbose_name='Адрес электронной почты',
        unique=True)
    first_name = models.CharField(
        max_length=USER_MAX_LENGTH,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=USER_MAX_LENGTH,
        verbose_name='Фамилия'
    )

    avatar = models.ImageField(
        upload_to='media/avatars/',
        blank=True,
        null=True,
        default=None,
        verbose_name='avatar'
    )

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username[:TEXT_LIMIT]


class Tag(models.Model):
    name = models.CharField(
        max_length=MAX_LENGTH,
        verbose_name='Название тэга',
        unique=True
    )
    color = ColorField(
        format='hex',
        max_length=COLOR_MAX_LENGTH,
        unique=True,
        verbose_name='Код цвета',
        validators=[
            RegexValidator(regex=r'^#([A-Fa-f0-9]{6})$')
        ],
    )
    slug = models.SlugField(
        verbose_name='Слаг тэга',
        max_length=MAX_LENGTH,
        unique=True,
    )

    class Meta:
        ordering = ('name',)
        default_related_name = 'tags'
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'slug'),
                name='unique_tag'
            ),
        )

    def __str__(self):
        return self.name[:TEXT_LIMIT]


class Ingredient(models.Model):
    name = models.CharField(
        max_length=MAX_LENGTH,
        verbose_name='Название',
    )
    measurement_unit = models.CharField(
        max_length=MAX_LENGTH,
        verbose_name='Единица измерения'
    )

    class Meta:
        ordering = ('name',)
        default_related_name = 'ingredients'
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_ingredient'
            ),
        )

    def __str__(self):
        return f'{self.name[:TEXT_LIMIT]} {self.measurement_unit[:4]}'


class Recipe(models.Model):
    author = models.ForeignKey(
        FoodgramUser,
        verbose_name='Автор',
        on_delete=models.CASCADE,
    )
    name = models.CharField(
        max_length=MAX_LENGTH,
        verbose_name='Название рецепта'
    )
    text = models.TextField(verbose_name='Описание')
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления (в минутах)',
        validators=[
            MinValueValidator(MIN_VALUE, message=MIN_MESSAGE)
        ]
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэги'
    )
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='media/images/',
        default=None,
    )
    published_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ('-published_at',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        default_related_name = 'recipes'

    def __str__(self):
        return self.name[:TEXT_LIMIT]


class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE
    )
    amount = models.PositiveIntegerField(
        verbose_name='Мера',
        validators=[
            MinValueValidator(MIN_VALUE, message=MIN_MESSAGE)
        ]
    )

    class Meta:
        default_related_name = 'recipe_ingredients'
        verbose_name = 'Продукт для рецепта'
        verbose_name_plural = 'Продукты для рецепта'

    def __str__(self):
        return f'{self.ingredient} {self.recipe}'


class Subscription(models.Model):
    subscribed_to = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        related_name='authors'
    )
    subscriber = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        related_name='subscribers'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['subscriber', 'subscribed_to'],
                name='unique_subscribtion'
            )
        ]

    def __str__(self):
        return (
            f'{self.subscriber.username}'
            f' подписан на {self.subscribed_to.username}'
        )


class UserRecipeModel(models.Model):
    "Базовая модель для избранного и корзины покупок."
    user = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='%(class)s_unique_recipe_'
            )
        ]
        default_related_name = '%(class)ss'

    def __str__(self):
        return f'{self.user} {self.recipe}'


class Favorite(UserRecipeModel):

    class Meta(UserRecipeModel.Meta):
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'


class ShoppingCart(UserRecipeModel):

    class Meta(UserRecipeModel.Meta):
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
