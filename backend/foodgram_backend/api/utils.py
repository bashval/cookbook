from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from recipes.models import Recipe
# from .serializers import FavoriteRecipeSerializer

User = get_user_model()


def favorite_shoppingcart_handler(request, pk, model, serializer_class):
    recipe = get_object_or_404(Recipe, id=pk)
    user = request.user
    if request.method == 'POST':
        if model.objects.filter(recipe=recipe, user=user).exists():
            return Response(
                {'detail': 'Рецепт уже был добавлен ранее.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        new_instance = model(recipe=recipe, user=user)
        new_instance.save()
        serializer = serializer_class(recipe)
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == 'DELETE':
        instance = get_object_or_404(model, recipe=recipe, user=user)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


def get_user_related_recipes(user, related_name):
    if not user.is_authenticated:
        return []
    lookup = '__'.join([related_name, 'user'])
    recipes = Recipe.objects.filter(**{lookup: user})
    return list(recipes)