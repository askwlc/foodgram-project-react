from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, status

from recipes.models import (Cart, Favorite, Ingredient, Recipe,
                            RecipeIngredient, Tag)
from users.models import Follow, User


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор модели User."""

    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'password', 'is_subscribed')
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


class ShortRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения рецептов в FollowSerializer."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор подписок."""
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.BooleanField(default=True, read_only=True)
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = ('email', 'id',
                  'username', 'first_name',
                  'last_name', 'is_subscribed',
                  'recipes', 'recipes_count')

    def get_recipes(self, obj):
        """Отображение рецептов."""
        request = self.context.get('request')
        recipes = obj.author.recipes.all()
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit:
            try:
                recipes = recipes[:int(recipes_limit)]
            except ValueError:
                raise serializers.ValidationError({
                    'errors': 'recipes_limit должен быть числом'})
        return ShortRecipeSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        """Отображение количества рецептов."""
        return obj.author.recipes.count()


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор связной модели RecipeIngredient."""
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(
        source='ingredient.name',
        read_only=True
    )
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', read_only=True
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeListSerializer(serializers.ModelSerializer):
    """Сериализатор просмотра рецептов."""
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        many=True, source='recipe_ingredients'
    )
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )

    def get_is_favorited(self, obj):
        """Проверяет авторизацию при добавлении рецепта."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.favorites.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        """Проверяет авторизацию при добавлении в корзину."""
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return user.cart_recipe.filter(recipe=obj).exists()


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания рецептов."""
    ingredients = RecipeIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(many=True,
                                              queryset=Tag.objects.all())
    image = Base64ImageField(required=False)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'name',
            'image', 'text', 'cooking_time'
        )
        read_only_fields = ('author',)

    def to_representation(self, instance):
        return RecipeListSerializer(
            instance,
            context=self.context).data

    def create_new_ingredients(
            self, new_recipe,
            new_ingredients):
        """Вспомогательный метод для создания
        объектов модели RecipeIngredient.
        """
        ingredients = []
        for ingredient in new_ingredients:
            ingredient_id = ingredient.get('ingredient', {}).get('id')

            recipe_ingredient = RecipeIngredient(
                recipe=new_recipe,
                ingredient_id=ingredient_id,
                amount=ingredient["amount"],
            )
            ingredients.append(recipe_ingredient)

        RecipeIngredient.objects.bulk_create(ingredients)

    def create(self, validated_data):
        """Создание рецепта."""
        tags = validated_data.pop("tags")
        request_user = self.context["request"].user
        ingredients = validated_data.pop("ingredients")
        new_recipe = Recipe.objects.create(
            author=request_user, **validated_data
        )

        self.create_new_ingredients(new_recipe, ingredients)
        new_recipe.tags.add(*tags)
        return new_recipe

    def update(self, instance: Recipe, validated_data):
        """Обновление рецепта."""
        RecipeIngredient.objects.filter(recipe=instance).delete()
        self.create_new_ingredients(
            instance, validated_data.pop("ingredients")
        )
        tags = validated_data.pop("tags")
        instance.tags.set(tags, clear=True)
        return super().update(instance, validated_data)

    def validate(self, value):
        """Валидация данных при создании и обновлении рецепта."""
        ingredients = value.get('ingredients')
        if ingredients is None:
            raise serializers.ValidationError(
                'Список ингредиентов не может быть пустым.'
            )
        ingredients_id_list = []
        for item in ingredients:
            if item['amount'] == 0:
                raise serializers.ValidationError(
                    'Количество ингредиента не может быть равным нулю.'
                )
            # Access `ingredient.id` instead of just `id`
            ingredient_id = item.get('ingredient', {}).get('id')
            if ingredient_id in ingredients_id_list:
                raise serializers.ValidationError(
                    'Указано несколько одинаковых ингредиентов.'
                )
            ingredients_id_list.append(ingredient_id)
        return value


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор избранных рецептов."""
    id = serializers.ReadOnlyField(source='recipe.id')
    name = serializers.ReadOnlyField(source='recipe.name')
    image = serializers.SerializerMethodField()
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        model = Favorite
        fields = ('id', 'name', 'image', 'cooking_time')

    def get_image(self, obj):
        return obj.recipe.image.url


class CartSerializer(serializers.ModelSerializer):
    """Сериализатор добавления рецепта в корзину."""
    name = serializers.ReadOnlyField(source='recipe.name')
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')
    image = serializers.ImageField(source='recipe.image', read_only=True)

    class Meta:
        model = Cart
        fields = ("id", "name", "image", "cooking_time")

    def validate(self, data):
        """Проверка добавления рецепта дважды."""
        recipe = self.instance
        user = self.context.get('request').user
        if Cart.objects.filter(recipe=recipe, user=user).exists():
            raise serializers.ValidationError(
                detail='Рецепт уже добавлен в корзину.',
                code=status.HTTP_400_BAD_REQUEST,
            )
        return data
