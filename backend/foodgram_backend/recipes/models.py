from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .constants import (INGREDIENT_NAME_LENGTH, MAX_COOKING_TIME,
                        MIN_COOKING_TIME, MIN_IGREDIENT_AMOUNT,
                        RECIPE_NAME_LENGTH, TAG_NAME_LENGTH, TAG_SLUG_LENGTH,
                        UNIT_NAME_LENGTH)

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        'Название', max_length=INGREDIENT_NAME_LENGTH)
    measurement_unit = models.CharField(
        'Единицы измерения', max_length=UNIT_NAME_LENGTH)

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name', 'id']

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class Tag(models.Model):
    name = models.CharField(
        'Название', max_length=TAG_NAME_LENGTH, unique=True)
    slug = models.CharField(
        'Идентификатор', max_length=TAG_SLUG_LENGTH, unique=True)

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'
        ordering = ['name', 'id']

    def __str__(self):
        return f'{self.name}'


class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='Автор')
    name = models.CharField('Haзвание', max_length=RECIPE_NAME_LENGTH)
    image = models.ImageField(
        'Картинка', upload_to='recipes/images/')
    text = models.TextField(verbose_name='Описание')
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredient', verbose_name='Ингредиенты')
    tags = models.ManyToManyField(
        Tag, through='RecipeTag', verbose_name='Тег')
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[
            MaxValueValidator(
                MAX_COOKING_TIME,
                message=('Время приготовления не может'
                         f'превышать {MAX_COOKING_TIME}')
            ),
            MinValueValidator(
                MIN_COOKING_TIME,
                message=('Время приготовления не может быть'
                         f'меньше {MIN_COOKING_TIME} минуты')
            )
        ]
    )
    pub_date = models.DateTimeField(
        'Дата публикации', auto_now_add=True)

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'Рецепты'
        default_related_name = 'recipes'
        ordering = ['-pub_date', 'id']

    def __str__(self):
        return f'{self.name}'


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Рецепт')
    tag = models.ForeignKey(
        Tag, on_delete=models.CASCADE, verbose_name='Тег')

    class Meta:
        verbose_name = 'тег рецепта'
        verbose_name_plural = 'Теги рецептов'
        constraints = [
            models.UniqueConstraint(
                fields=['tag', 'recipe'], name='unique_tag_for_recipe')
        ]

    def __str__(self):
        return f'{self.recipe.name}, {self.tag.name}'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Рецепт')
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, verbose_name='Ингредиент')
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[
            MinValueValidator(
                MIN_IGREDIENT_AMOUNT,
                message=('Количество ингредиента не может быть'
                         f'меньше {MIN_IGREDIENT_AMOUNT}.')
            )
        ]
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique_ingredient_in_recipe'
            )
        ]

    def __str__(self):
        return (
            f'{self.ingredient.name} - {self.amount}'
            f'({self.ingredient.measurement_unit}) - {self.recipe.name}'
        )


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='favorite_recipes')
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='is_favorited')

    class Meta:
        verbose_name = 'избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_recipe_in_favorite')
        ]

    def __str__(self):
        return (
            f'"{self.recipe.name}" в избраном '
            f'для пользователя {self.user}'
        )


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='shopping_cart')
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_query_name='is_in_shopping_cart',
        related_name='in_shopping_cart'
    )

    class Meta:
        verbose_name = 'список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_recipe_in_cart')
        ]

    def __str__(self):
        return (
            f'"{self.recipe.name}" в списке покупок '
            f'пользователя {self.user}'
        )
