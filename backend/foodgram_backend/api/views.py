from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet

from recipes.models import Ingredient, Recipe, Tag, RecipeIngredient
from .filters import IngredientFilter, RecipeFilter
from .serializers import (
    IngredientSerializer, RecipeSerializer, TagSerializer, AmountSerializer)

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
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()
    http_method_names = ['get', 'post', 'patch', 'delete']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = False
        return self.update(request, *args, **kwargs)
    
    @action(methods=['get'], detail=True, url_path='get-link')
    def get_link(self, request):
        pass


class TestViewSet(ModelViewSet):
    pagination_class = None
    serializer_class = AmountSerializer
    queryset = RecipeIngredient.objects.all()
