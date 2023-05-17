from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint

from users.models import User


class Recipe(models.Model):
    """Модель рецептов"""
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes', verbose_name='Автор рецепта')
    name = models.CharField(max_length=200, verbose_name='Название рецепта')
    text = models.TextField(verbose_name='Описание рецепта')
    image = models.ImageField(upload_to='recipes/images', blank=True, null=True)
    cooking_time = models.IntegerField(
        validators=[MinValueValidator(1, message='Время приготовления должно быть больше 1 минуты.')],
        verbose_name='Время приготовления')
    ingredients = models.ManyToManyField('Ingredient', through='RecipeIngredient', related_name='recipes',
                                         verbose_name='Ингредиент')
    tags = models.ManyToManyField('Tag', related_name='recipes', verbose_name='Тег')

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиентов"""
    name = models.CharField(max_length=200, verbose_name='Название ингредиента')
    measurement_unit = models.CharField(max_length=200, verbose_name='Единица измерения')

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Промежуточная модель Рецепт - Ингредиент"""
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='recipe_ingredients')
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, verbose_name='Ингредиент')
    amount = models.FloatField(
        validators=[MinValueValidator(1, message='Количество ингредиентов должно быть больше 1')],
        verbose_name='Количество ингредиента')

    class Meta:
        constraints = [
            UniqueConstraint(fields=['recipe', 'ingredient'], name='unique_ingredient_for_recipe')
        ]


class Tag(models.Model):
    """Модель тегов"""
    name = models.CharField(max_length=200, verbose_name='Название тега')
    color = models.CharField(max_length=7, blank=True, null=True, verbose_name='Цвет в HEX')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='Уникальный слаг')

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Favorite(models.Model):
    """Модель рецептов добавленных в избранное"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='favorites')

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'], name='unique_recipe_in_favorites')
        ]


class Cart(models.Model):
    """Модель корзины для покупок"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='cart')

    class Meta:
        verbose_name = 'Рецепт в корзине'
        verbose_name_plural = 'Рецепты в корзине'
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'], name='unique_recipe_in_cart')
        ]
