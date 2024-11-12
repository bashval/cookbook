from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect
from django.utils.crypto import get_random_string
from django.utils.http import urlencode
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet

from recipes.models import Ingredient, Recipe, Tag, RecipeIngredient
from .constants import SHORT_LINK_LENGTH
from .filters import IngredientFilter, RecipeFilter
from .models import ShortLinkRecipe
from .serializers import (
    IngredientSerializer, RecipeSerializer, TagSerializer, ShortLinkSerializer)

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
    def get_link(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        while True:
            url_slug = get_random_string(length=SHORT_LINK_LENGTH)
            if not ShortLinkRecipe.objects.filter(url_slug=url_slug).exists():
                break
        short_link = ShortLinkRecipe(recipe=recipe, url_slug=url_slug)
        short_link.save()

        relative_url = reverse(
            'short_link_redirect', kwargs={'slug': url_slug})
        short_link_url = request.build_absolute_uri(relative_url)
        data = {'short_link': short_link_url}
        serializer = ShortLinkSerializer(data=data)
        serializer.is_valid()
        return Response(serializer.data, status=status.HTTP_200_OK)


def short_link_redirect(request, slug):
    link = get_object_or_404(ShortLinkRecipe, url_slug=slug)
    return redirect('recipe-detail', pk=link.recipe.id)


class TestViewSet(ModelViewSet):
    pagination_class = None
    # serializer_class = AmountSerializer
    queryset = RecipeIngredient.objects.all()
