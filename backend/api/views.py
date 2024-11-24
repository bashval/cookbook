from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from djoser.permissions import CurrentUserOrAdmin
from djoser.views import UserViewSet as BaseUserViewSet
from recipes.models import (
    FavoriteRecipe, Ingredient, Recipe, RecipeIngredient, ShoppingCart, Tag
)
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticated, IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from users.models import Subscription
from .filters import IngredientFilter, RecipeFilter
from .mixins import UserRelatedModelMixin
from .models import ShortLink
from .permissions import IsOwnerOrReadOnly
from .serializers import (
    AvatarSerializer, FavoriteRecipeSerializer, IngredientSerializer,
    RecipeCreateSerializer, RecipeReadSerializer, ShoppingCartSerialiser,
    ShortLinkSerializer, ShortRecipeSerializer, SubscriptionReadSerializer,
    SubscriptionSerializer, TagSerializer
)
from .utils import create_short_link, get_pdf_shopping_list

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
    permission_classes = [IsOwnerOrReadOnly, IsAuthenticatedOrReadOnly]
    serializer_class = RecipeCreateSerializer
    queryset = Recipe.objects.all().prefetch_related(
        'is_favorited', 'in_shopping_cart'
    )
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action == 'favorite' or self.action == 'shopping_cart':
            return ShortRecipeSerializer
        elif self.request.method == 'GET':
            return RecipeReadSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = False
        return self.update(request, *args, **kwargs)

    @action(methods=['get'], detail=True, url_path='get-link')
    def get_link(self, request, pk):
        short_link = create_short_link(request, pk)
        serializer = ShortLinkSerializer(short_link)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(['get'], detail=False, permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        ingredients_amounts = (
            RecipeIngredient.objects.filter(
                recipe__is_in_shopping_cart__user=request.user
            ).values(
                'ingredient__name',
                'ingredient__measurement_unit'
            ).annotate(Sum('amount'))
        )
        file = get_pdf_shopping_list(ingredients_amounts)
        return FileResponse(
            file, as_attachment=True, filename='shopping_list.pdf')


class FavoriteRecipeViewSet(UserRelatedModelMixin):
    queryset = FavoriteRecipe.objects.all()
    serializer_class = FavoriteRecipeSerializer
    ralated_object_model = Recipe
    related_object_field_name = 'recipe'


class ShoppingCartViewSet(UserRelatedModelMixin):
    queryset = ShoppingCart.objects.all()
    serializer_class = ShoppingCartSerialiser
    ralated_object_model = Recipe
    related_object_field_name = 'recipe'


class SubscriptionViewSet(UserRelatedModelMixin):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    ralated_object_model = User
    related_object_field_name = 'subscribing'


def short_link_redirect(request, slug):
    link = get_object_or_404(ShortLink, short_link_slug=slug)
    return redirect(link.redirect_url)


class UsersViewSet(BaseUserViewSet):

    def get_serializer_class(self):
        if self.action == 'avatar':
            return AvatarSerializer
        elif self.action == 'subscriptions':
            return SubscriptionReadSerializer
        return super().get_serializer_class()

    @action(methods=['put', 'delete'], detail=False, url_path='me/avatar')
    def avatar(self, request):
        instance = self.get_instance()
        if request.method == 'PUT':
            serializer = self.get_serializer(
                instance=instance, data=request.data, partial=False
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        elif request.method == 'DELETE':
            instance.avatar = None
            instance.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(['get'], detail=False, permission_classes=[CurrentUserOrAdmin])
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        if request.method == 'GET':
            return self.retrieve(request, *args, **kwargs)

    @action(['get'], detail=False, permission_classes=(IsAuthenticated, ))
    def subscriptions(self, request):
        self.queryset = User.objects.filter(subscribing__user=request.user)
        return self.list(request)
