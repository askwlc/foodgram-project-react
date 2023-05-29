from django.contrib import admin
from .models import (Recipe, Favorite, Ingredient, RecipeIngredient, Tag, Cart)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'favorites_count',)
    list_filter = ('author', 'name', 'tags',)

    def favorites_count(self, obj):
        return Favorite.objects.filter(recipe=obj).count()

    favorites_count.short_description = 'Число добавлений этого рецепта в избранное.'


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    list_filter = ('name',)


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'color',)
    list_filter = ('name',)


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
