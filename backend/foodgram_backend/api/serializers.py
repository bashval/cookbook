from django.contrib.auth import get_user_model
from rest_framework import serializers

from recipes.models import Ingredient, RecipeIngredient, Recipe, Tag
from users.serializers import UserReadSerializer

User = get_user_model()


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class RecipeIngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'

    def serialize_amount(self, recipe_instance):
        amount_instance = (recipe_instance
                           .recipeingredient_set
                           .filter(recipe=self.context['recipe_instance'])
                           .first()
                           )
        if amount_instance:
            return AmountSerializer(amount_instance).data
        return {}

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        return {**rep, **self.serialize_amount(instance)}


class AmountSerializer(serializers.ModelSerializer):

    class Meta:
        model = RecipeIngredient
        fields = ('amount',)


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = UserReadSerializer(required=False)
    # ingredients = serializers.SerializerMethodField()
    ingredients = IngredientSerializer(many=True)

    class Meta:
        model = Recipe
        fields = '__all__'

    # def get_ingredients(self, recipe):
    #     return RecipeIngredientSerializer(
    #         recipe.ingredients.all(),
    #         many=True,
    #         context={'recipe_instance': recipe}
    #     ).data
