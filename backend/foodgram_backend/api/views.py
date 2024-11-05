from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ReadOnlyModelViewSet

from recipes.models import Ingredient, Tag
from .filters import IngredientFilter
from .serializers import IngredientSerializer, TagSerializer

User = get_user_model()


class IngredientViewSet(ReadOnlyModelViewSet):
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    # filter_fields = ('name__startswith',) #icontains
    pagination_class = None
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()


class TagViewSet(ReadOnlyModelViewSet):
    pagination_class = None
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
