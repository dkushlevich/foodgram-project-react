from rest_framework import serializers
from django.contrib.auth import get_user_model
from djoser.serializers import (
    UserCreateSerializer as DjoserUserCreateSerializer
)
from djoser.serializers import UserSerializer as DjoserUserSerializer
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator

from api.fields import Base64ImageField
from api.mixins import ShortRecipeRepresentationMixin
from api.utils import collect_ingredientsrecipe_objects, collect_tags
from recipes.models import (
    Favorite, Ingredient, IngredientRecipe, Purchase,
    Recipe, Tag
)
from users.models import Subscription


User = get_user_model()


class UserCreateSerializer(DjoserUserCreateSerializer):

    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            User.USERNAME_FIELD,
            'password',
            'id'
        )
        read_only_fields = ('id', )


class UserSerializer(DjoserUserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            User.USERNAME_FIELD,
            'id',
            'is_subscribed'
        )
        read_only_fields = ('is_subscribed',)

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        return (
            not user.is_anonymous and
            Subscription.objects.filter(user=user, author=obj).exists()
        )


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        setattr(self.Meta, 'read_only_fields', [*self.fields])

    def to_internal_value(self, data):
        if not isinstance(data, int) or data < 1:
            raise serializers.ValidationError(
                'Убедитесь, что это значение больше либо равно 1.'
            )
        return data


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit.name'
    )

    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'amount', 'measurement_unit')
        read_only_fields = ('name', 'measurement_unit')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['id'] = instance.ingredient.id
        return representation


class IngredientSerializer(serializers.ModelSerializer):
    measurement_unit = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True
    )

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(default=serializers.CurrentUserDefault())
    tags = TagSerializer(many=True)
    ingredients = IngredientRecipeSerializer(many=True, required=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        exclude = ('pub_date', )

    def is_authenticated(func):
        def wrapper(self, obj):
            if self.context.get('request').user.is_anonymous:
                return False
            return func(self, obj)
        return wrapper

    @is_authenticated
    def get_is_in_shopping_cart(self, obj):
        return Purchase.objects.filter(
            user=self.context.get('request').user,
            recipe=obj
        ).exists()

    @is_authenticated
    def get_is_favorited(self, obj):
        return Favorite.objects.filter(
            user=self.context.get('request').user,
            recipe=obj
        ).exists()

    def validate_ingredients(self, data):
        if len(data) == 0:
            raise ValidationError(
                'Список ингредиентов не может быть пустым.'
            )
        ingredients_serializer = IngredientRecipeSerializer(
            data=data,
            many=True
        )
        ingredients_serializer.is_valid(raise_exception=True)
        return data

    def validate_tags(self, data):
        if len(data) == 0:
            raise ValidationError(
                'Список тегов не может быть пустым.'
            )
        return super().validate(data)

    def create(self, validated_data):
        tag_data = validated_data.pop('tags')
        ingredient_data = validated_data.pop('ingredients')
        recipe = Recipe(**validated_data)
        ingredientrecipe_objects = collect_ingredientsrecipe_objects(
            ingredient_data, recipe
        )
        tags = collect_tags(tag_data)
        recipe.save()
        IngredientRecipe.objects.bulk_create(
            ingredientrecipe_objects
        )
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.image = validated_data.get('image', instance.image)
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time
        )

        if 'ingredients' in validated_data:
            ingredients = validated_data.get('ingredients')
            IngredientRecipe.objects.filter(recipe=instance).delete()
            IngredientRecipe.objects.bulk_create(
                collect_ingredientsrecipe_objects(
                    ingredients,
                    instance
                )
            )

        if 'tags' in validated_data:
            tags = collect_tags(validated_data.get('tags'))
            instance.tags.set(tags)
        instance.save()
        return instance


class FavoriteSerializer(
    ShortRecipeRepresentationMixin,
    serializers.ModelSerializer
):

    class Meta:
        model = Favorite
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=['user', 'recipe']
            )
        ]


class PurchaseSerializer(
    ShortRecipeRepresentationMixin, serializers.ModelSerializer
):

    class Meta:
        model = Purchase
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Purchase.objects.all(),
                fields=['user', 'recipe']
            )
        ]


class RecipeShortSerializer(serializers.ModelSerializer):
    image = Base64ImageField(read_only=True)
    name = serializers.ReadOnlyField()
    cooking_time = serializers.ReadOnlyField()

    class Meta:
        model = Recipe
        fields = ('id', 'name',
                  'image', 'cooking_time')


class SubscriptionSerializer(
    serializers.ModelSerializer
):
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = (
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
        read_only_fields = fields

    def get_recipes_count(self, obj):
        return obj.author.recipes.count()

    def get_recipes(self, obj):
        serializer = RecipeShortSerializer(obj.author.recipes, many=True)
        request = self.context.get('request')
        recipes_limit = (
            request.parser_context['request'].
            query_params.get('recipes_limit')
        )
        recipes = obj.author.recipes.all()
        if recipes_limit:
            try:
                recipes = recipes[:int(recipes_limit)]
            except ValueError:
                raise ValidationError({
                    'errors': (
                        'recipes_limit - целое положительное число'
                    )
                })
            except AssertionError:
                raise ValidationError({
                    'errors': (
                        'recipes_limit - целое положительное число'
                    )
                })
        serializer = RecipeShortSerializer(recipes, many=True)
        return serializer.data

    def get_is_subscribed(self, obj):
        return True

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['id'] = instance.author.id
        representation['username'] = instance.author.username
        representation['email'] = instance.author.email
        representation['first_name'] = instance.author.first_name
        representation['last_name'] = instance.author.last_name
        return representation
