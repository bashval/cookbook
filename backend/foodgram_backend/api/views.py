from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet

from recipes.models import Ingredient, Recipe, Tag, RecipeIngredient
from .filters import IngredientFilter
from .serializers import IngredientSerializer, RecipeSerializer, TagSerializer, RecipeIngredientSerializer, AmountSerializer

User = get_user_model()


class IngredientViewSet(ReadOnlyModelViewSet):
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()


class TagViewSet(ReadOnlyModelViewSet):
    pagination_class = None
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class RecipeViewSet(ModelViewSet):
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()


class TestViewSet(ModelViewSet):
    pagination_class = None
    serializer_class = AmountSerializer
    queryset = RecipeIngredient.objects.all()
