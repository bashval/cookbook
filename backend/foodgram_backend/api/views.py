from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect
from django.utils.crypto import get_random_string
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.permissions import CurrentUserOrAdmin
from djoser.views import UserViewSet as BaseUserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet

from recipes.models import (
    Ingredient, FavoriteRecipe, Recipe, ShoppingCart, Tag)
from users.models import Subscription
from .constants import SHORT_LINK_LENGTH
from .filters import IngredientFilter, RecipeFilter
from .models import ShortLinkRecipe
from .permissions import IsOwnerOrReadOnly
from .serializers import (
    AvatarSerializer, IngredientSerializer, RecipeSerializer,
    ShortLinkSerializer, ShortRecipeSerializer, TagSerializer, SubscribeUserSerializer)
from .utils import user_related_model_request_handler, create_related_model_instance, delete_related_model_instance

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
    permission_classes = [IsOwnerOrReadOnly, ]
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action == 'favorite' or self.action == 'shopping_cart':
            return ShortRecipeSerializer
        return super().get_serializer_class()

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

    @action(methods=['post', 'delete'], detail=True)
    def favorite(self, request, pk):
        recipe = get_object_or_404(self.get_queryset(), pk=pk)
        return user_related_model_request_handler(
            request=request,
            obj=recipe,
            serializer=self.get_serializer(recipe),
            model=FavoriteRecipe,
        )

    @action(methods=['post', 'delete'], detail=True)
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(self.get_queryset(), pk=pk)
        current_user = request.user
        if request.method == 'POST':
            create_related_model_instance(
                model=ShoppingCart,
                objects=(recipe, current_user)
            )
            return self.retrieve(request)
        elif request.method == 'DELETE':
            delete_related_model_instance(
                model=ShoppingCart,
                objects=(recipe, current_user)
            )
            return Response(status=status.HTTP_204_NO_CONTENT)
        # return user_related_model_request_handler(
        #     request=request,
        #     obj=recipe,
        #     serializer=self.get_serializer(recipe),
        #     model=ShoppingCart
        # )


def short_link_redirect(request, slug):
    link = get_object_or_404(ShortLinkRecipe, url_slug=slug)
    return redirect('recipe-detail', pk=link.recipe.id)


class UsersViewSet(BaseUserViewSet):

    def get_serializer_class(self):
        if self.action == 'avatar':
            return AvatarSerializer
        elif self.action == 'subscribe' or self.action == 'subscriptions':
            return SubscribeUserSerializer
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
        if request.method == "GET":
            return self.retrieve(request, *args, **kwargs)

    @action(['post', 'delete'], detail=True)
    def subscribe(self, request, id):
        user_to_subscribe = get_object_or_404(self.get_queryset(), id=id)
        current_user = request.user

        if current_user == user_to_subscribe:
            raise ValidationError('Нелья подписаться на самого себя.')
        objects = ({'subscribing': user_to_subscribe}, current_user)

        if request.method == 'POST':
            create_related_model_instance(model=Subscription, objects=objects)
            return self.retrieve(request)

        elif request.method == 'DELETE':
            delete_related_model_instance(model=Subscription, objects=objects)
            return Response(status=status.HTTP_204_NO_CONTENT)
        # return user_related_model_request_handler(
        #     request=request,
        #     obj=following_user,
        #     serializer=self.get_serializer(following_user),
        #     model=Subscription,
        #     lookup_name='subscribing',

    @action(['get'], detail=False, permission_classes=(IsAuthenticated, ))
    def subscriptions(self, request):
        self.queryset = User.objects.filter(subscribing__user=request.user)
        # qs = User.objects.filter(subscriptions__subscribing=request.user)
        # qs = User.objects.filter(subscribing__user=request.user)
        # self.queryset = request.user.subscriptions.values('subscribing')
        # print('__________QS__________', qs)
        return self.list(request)
