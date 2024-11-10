from django.contrib.auth import get_user_model
from rest_framework import serializers

from recipes.models import (
    Ingredient, Recipe, RecipeIngredient, RecipeTag, Tag)
from users.serializers import Base64ImageField, UserReadSerializer

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


class RecIngCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all(), required=True
    )
    author = UserReadSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = RecIngCreateSerializer(many=True, write_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        exclude = ('pub_date',)

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get('request', None)
        if request and getattr(request, 'method', None) == 'PATCH':
            fields['image'].required = False
        return fields

    def get_is_favorited(self, obj):
        current_user = self.context['request'].user
        if current_user.is_authenticated:
            return obj in current_user.favorite_recipes.all()
        return False

    def get_is_in_shopping_cart(self, obj):
        current_user = self.context['request'].user
        if current_user.is_authenticated:
            return obj in current_user.shopping_cart.all()
        return False

    def to_representation(self, recipe_instance):
        ret = super().to_representation(recipe_instance)
        ret['ingredients'] = RecipeIngredientSerializer(
            recipe_instance.ingredients.all(),
            many=True,
            context={'recipe_instance': recipe_instance}
        ).data
        ret['tags'] = TagSerializer(
            Tag.objects.filter(id__in=ret['tags']), many=True).data
        return ret

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        for tag in tags:
            RecipeTag.objects.create(recipe=recipe, tag=tag)
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            )
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.tags.set(tags)
        instance.ingredients.clear()
        for ingredient in ingredients:
            instance.ingredients.add(
                ingredient['id'],
                through_defaults={'amount': ingredient['amount']}
            )
        instance.save()
        return instance

    def validate_tags(self, values):
        if not values:
            raise serializers.ValidationError('Это поле не может быть пустым.')
        if values != list(set(values)):
            message = 'У рецепта не могут быть повторяющиеся теги.'
            raise serializers.ValidationError(message)
        return values

    def validate_ingredients(self, values):
        if not values:
            raise serializers.ValidationError('Это поле не может быть пустым.')
        ingredients_id = [value['id'] for value in values]
        if ingredients_id != list(set(ingredients_id)):
            message = 'В рецепте не могут повторяться ингредиенты.'
            raise serializers.ValidationError(message)
        return values


class RecipeReadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, required=True)
    author = UserReadSerializer(required=False)
    image = Base64ImageField()
    ingredients = serializers.SerializerMethodField()
    # ingredients = IngredientSerializer(many=True)

    class Meta:
        model = Recipe
        fields = '__all__'

    def get_ingredients(self, recipe):
        return RecipeIngredientSerializer(
            recipe.ingredients.all(),
            many=True,
            context={'recipe_instance': recipe}
        ).data

    # def validate_tags(self, values):
    #     instancies = []
    #     for value in values:
    #         try:
    #             instance = Tag.objects.get(id=value)
    #         except Tag.DoesNotExist:
    #             raise serializers.ValidationError('No such tag.')
    #         instancies.append(instance)
    #     print('____________HEY_______', instancies)
    #     return instancies
