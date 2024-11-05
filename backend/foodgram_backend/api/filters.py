from django.db.models import Q
from django_filters.rest_framework import CharFilter, FilterSet

from recipes.models import Ingredient


class IngredientFilter(FilterSet):
    name = CharFilter(field_name='name', lookup_expr='istartswith')
    # name = CharFilter(field_name='name', method='name_filter')

    class Meta:
        model = Ingredient
        fields = ['name',]

    # def name_filter(self, queryset, name, value):
    #     return queryset.filter(Q(name__istartswith=value) | Q(name__icontains=value))
