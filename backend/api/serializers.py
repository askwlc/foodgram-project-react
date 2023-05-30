from rest_framework import serializers

from recipes.models import Tag, Recipe, Ingredient, Favorite, RecipeIngredient, Cart
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор модели User."""

    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'password', 'is_subscribed')
        extra_kwargs = {'password': {'write_only': True}}
        read_only_fields = ("is_subscribed",)

    def get_is_subscribed(self, obj):
        """Проверяет подписку на текущего пользователя."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.follower.filter(author=obj).exists()

    def create(self, validated_data):
        """Создаёт пользователя."""
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def to_representation(self, instance):
        """Убирает is_subscribed при создании."""
        show = super().to_representation(instance)
        if self.context['request'].method == 'POST':
            show.pop('is_subscribed', None)
        return show


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор тегов."""
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор ингредиентов."""
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
        read_only_fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор связной модели RecipeIngredient."""
    ingredient = IngredientSerializer()

    class Meta:
        model = RecipeIngredient
        fields = ('recipe', 'ingredient', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор модели Recipe."""
    ingredients = RecipeIngredientSerializer(many=True)
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_cart', 'name', 'image', 'text', 'cooking_time'
        )

    def get_is_favorited(self, obj):
        """Проверяет добавлен ли рецепт в избранное
        у авторизованного пользователя."""
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Favorite.objects.filter(recipe=obj, user=request.user).exists()

    def get_is_in_cart(self, obj):
        """Проверяет добавлен ли рецепт в корзину
        у авторизованного пользователя."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Cart.objects.filter(recipe=obj, user=user).exists()

    # def get_ingredients(self, obj):
    #     queryset = IngredientInRecipe.objects.filter(recipe=obj)
    #     return IngredientInRecipeSerializer(queryset, many=True).data

class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ('id', 'name', 'image', 'cooking_time')
