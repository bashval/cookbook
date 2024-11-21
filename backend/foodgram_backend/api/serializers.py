import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from djoser.serializers import UserSerializer
from rest_framework import serializers

from .models import ShortLink
from recipes.models import (
    FavoriteRecipe, Ingredient, Recipe,
    RecipeIngredient, RecipeTag, ShoppingCart, Tag
)
from users.models import Subscription

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='image.' + ext)
        return super().to_internal_value(data)


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)


class UserReadSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'avatar', 'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        current_user = self.context['request'].user
        if not current_user.is_authenticated:
            return False
        return obj.subscribers.filter(user=current_user).exists()


class AmountSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeIngredient
        fields = ('amount',)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class RecipeIngredientReadSerializer(serializers.ModelSerializer):

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


class RecipeIngredientSerializer(serializers.ModelSerializer):
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
    ingredients = RecipeIngredientSerializer(many=True, write_only=True)
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
        user = self.context['request'].user
        if not user.is_authenticated:
            return False
        return obj.is_favorited.filter(user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if not user.is_authenticated:
            return False
        return obj.in_shopping_cart.filter(user=user).exists()

    def to_representation(self, recipe_instance):
        ret = super().to_representation(recipe_instance)
        ret['ingredients'] = RecipeIngredientReadSerializer(
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
        if len(values) != len(set(values)):
            message = 'У рецепта не могут быть повторяющиеся теги.'
            raise serializers.ValidationError(message)
        return values

    def validate_ingredients(self, values):
        if not values:
            raise serializers.ValidationError('Это поле не может быть пустым.')
        ingredients_id = [value['id'] for value in values]
        if len(ingredients_id) != len(set(ingredients_id)):
            message = 'В рецепте не могут повторяться ингредиенты.'
            raise serializers.ValidationError(message)
        return values


class ShortLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShortLink
        fields = ('short-link',)
        extra_kwargs = {
            'short-link': {'source': 'short_link_url'},
        }


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserRelatedBaseSerializer(serializers.ModelSerializer):

    def save(self, **kwargs):
        model = self.Meta.model
        if model.objects.filter(**kwargs).exists():
            raise serializers.ValidationError('Объект уже был добавлен ранее.')
        return super().save(**kwargs)


class UserRecipeBaseSerializer(UserRelatedBaseSerializer):

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret = ShortRecipeSerializer(Recipe.objects.get(id=ret['recipe'])).data
        return ret


class FavoriteRecipeSerializer(UserRecipeBaseSerializer):
    class Meta:
        model = FavoriteRecipe
        fields = '__all__'
        read_only_fields = ('user', 'recipe')


class ShoppingCartSerialiser(UserRecipeBaseSerializer):
    class Meta:
        model = ShoppingCart
        fields = '__all__'
        read_only_fields = ('user', 'recipe')


class SubscriptionSerializer(UserRelatedBaseSerializer):
    class Meta:
        model = Subscription
        fields = '__all__'
        read_only_fields = ('user', 'subscribing')

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret = SubscriptionReadSerializer(
            User.objects.get(id=ret['subscribing']), context=self.context).data
        return ret


class SubscriptionReadSerializer(UserReadSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count', 'avatar'
        )

    def get_recipes(self, obj):
        recipes_limit = self.context['request'].query_params.get(
            'recipes_limit', None)
        if recipes_limit:
            try:
                recipes_limit = int(recipes_limit)
            except ValueError:
                recipes_limit = None
        queryset = Recipe.objects.filter(author=obj)[:recipes_limit]
        return ShortRecipeSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()
