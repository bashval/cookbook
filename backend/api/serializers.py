import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from djoser.serializers import UserSerializer
from recipes.models import (
    FavoriteRecipe, Ingredient, Recipe, RecipeIngredient,
    RecipeTag, ShoppingCart, Tag,
)
from rest_framework import serializers

from users.models import Subscription
from recipes.constants import MIN_IGNREDIENT_AMOUNT
from .models import ShortLink

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
        return (
            current_user.is_authenticated
            and obj.subscribers.filter(user=current_user).exists()
        )


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient_id', read_only=True
    )
    name = serializers.SlugRelatedField(
        slug_field='name', source='ingredient', read_only=True
    )
    measurement_unit = serializers.SlugRelatedField(
        slug_field='measurement_unit', source='ingredient', read_only=True
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = UserReadSerializer(read_only=True)
    ingredients = RecipeIngredientReadSerializer(
        many=True, source='recipeingredient_set'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        exclude = ('pub_date',)

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return (
            user.is_authenticated
            and obj.is_favorited.filter(user=user).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return (
            user.is_authenticated
            and obj.in_shopping_cart.filter(user=user).exists()
        )


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(min_value=MIN_IGNREDIENT_AMOUNT)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeCreateSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all(), required=True
    )
    image = Base64ImageField()
    ingredients = RecipeIngredientCreateSerializer(many=True)

    class Meta:
        model = Recipe
        read_only_fields = ('author', )
        exclude = ('pub_date', )

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get('request', None)
        if request and getattr(request, 'method', None) == 'PATCH':
            fields['image'].required = False
        return fields

    def to_representation(self, instance):
        return RecipeReadSerializer(instance, context=self.context).data

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')

        recipe = Recipe.objects.create(**validated_data)
        RecipeTag.objects.bulk_create([
            RecipeTag(recipe=recipe, tag=tag) for tag in tags
        ])
        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            ) for ingredient in ingredients
        ])
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


class UserRecipeBaseSerializer(serializers.ModelSerializer):

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        return ShortRecipeSerializer(Recipe.objects.get(id=ret['recipe'])).data


class FavoriteRecipeSerializer(UserRecipeBaseSerializer):
    class Meta:
        model = FavoriteRecipe
        fields = ('user', 'recipe')
        validators = (
            serializers.UniqueTogetherValidator(
                queryset=FavoriteRecipe.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже добавлен в корзину.'
            ),
        )


class ShoppingCartSerialiser(UserRecipeBaseSerializer):
    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')
        validators = (
            serializers.UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже добавлен в корзину.'
            ),
        )


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ('user', 'subscribing')
        validators = (
            serializers.UniqueTogetherValidator(
                queryset=Subscription.objects.all(),
                fields=('user', 'subscribing'),
                message='Такая подписка уже существует.'
            ),
        )

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        return SubscriptionReadSerializer(
            User.objects.get(id=ret['subscribing']), context=self.context
        ).data

    def validate(self, attrs):
        if attrs['user'] == attrs['subscribing']:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя.'
            )
        return super().validate(attrs)


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
