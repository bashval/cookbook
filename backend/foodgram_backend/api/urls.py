from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    FavoriteRecipeViewSet, IngredientViewSet, RecipeViewSet,
    ShoppingCartViewSet, SubscriptionViewSet, TagViewSet, UsersViewSet
)


router_v1 = DefaultRouter()
router_v1.register(r'tags', TagViewSet)
router_v1.register(r'ingredients', IngredientViewSet)
router_v1.register(r'recipes', RecipeViewSet)
router_v1.register(r'users', UsersViewSet)

actions = {'delete': 'destroy', 'post': 'create'}

favorite_recipe_view = FavoriteRecipeViewSet.as_view(actions)
shopping_cart_view = ShoppingCartViewSet.as_view(actions)
subscription_view = SubscriptionViewSet.as_view(actions)

urlpatterns = [
    path('', include(router_v1.urls)),
    path('auth/', include('djoser.urls.authtoken')),
    path(
        'recipes/<int:obj_id>/favorite/',
        favorite_recipe_view,
        name='favorite_recipe'
    ),
    path(
        'recipes/<int:obj_id>/shopping_cart/',
        shopping_cart_view,
        name='shopping_cart'
    ),
    path(
        'users/<int:obj_id>/subscribe/',
        subscription_view,
        name='subscribe'
    )
]
