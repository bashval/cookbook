from django.db import models

from recipes.models import Recipe
from .constants import SHORT_LINK_LENGTH


class ShortLinkRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='short_links')
    url_slug = models.CharField(max_length=SHORT_LINK_LENGTH, unique=True)

    class Meta:
        verbose_name = 'короткая ссылка'
        verbose_name_plural = 'Короткие ссылки'

    def __str__(self):
        return f'{self.url_slug} - слаг ссылки на рецепт {self.recipe.name}'
