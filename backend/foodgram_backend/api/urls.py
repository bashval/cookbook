from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import IngredientViewSet, RecipeViewSet, TagViewSet, TestViewSet

router_v1 = DefaultRouter()
router_v1.register(r'tags', TagViewSet)
router_v1.register(r'ingredients', IngredientViewSet)
router_v1.register(r'recipes', RecipeViewSet)

router_v1.register(r'test', TestViewSet, basename='test')

urlpatterns = [
    path('', include(router_v1.urls))
]
