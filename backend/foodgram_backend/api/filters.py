from django.db.models import Q
from django_filters.rest_framework import CharFilter, FilterSet, NumberFilter, ModelMultipleChoiceFilter

from recipes.models import Ingredient, Recipe, Tag


class IngredientFilter(FilterSet):
    name = CharFilter(field_name='name', lookup_expr='istartswith')
    # name = CharFilter(field_name='name', method='name_filter')

    class Meta:
        model = Ingredient
        fields = ['name',]

    # def name_filter(self, queryset, name, value):
    #     return queryset.filter(Q(name__istartswith=value) | Q(name__icontains=value))


class RecipeFilter(FilterSet):
    author = NumberFilter(field_name='author')
    tags = ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tag.objects.all(),
        to_field_name='slug'
    )

    class Meta:
        model = Recipe
        fields = ['author', 'tags']

 # 'is_favorited', 'is_in_shopping_cart', 