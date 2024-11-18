from django.db.models import Q
from django_filters.rest_framework import (
    BooleanFilter, CharFilter, FilterSet,
    NumberFilter, ModelMultipleChoiceFilter
)

from recipes.models import Ingredient, Recipe, Tag


class IngredientFilter(FilterSet):
    name = CharFilter(field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ['name',]


class RecipeFilter(FilterSet):
    author = NumberFilter(field_name='author')
    tags = ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tag.objects.all(),
        to_field_name='slug'
    )
    is_favorited = BooleanFilter(method='filter_for_boolean')
    is_in_shopping_cart = BooleanFilter(method='filter_for_boolean')

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_favorited', 'is_in_shopping_cart']

    def filter_for_boolean(self, queryset, name, value):
        current_user = self.request.user
        if not current_user.is_authenticated:
            return queryset if not value else queryset.none()

        lookup = '__'.join([name, 'user'])
        if value:
            filter = Q(**{lookup: current_user})
        else:
            filter = ~Q(**{lookup: current_user})

        return queryset.filter(filter)
