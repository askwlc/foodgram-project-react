from rest_framework import serializers
# from recipes.models import Recipe, Tag, Ingredient, Favorite
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    """Обрабатывает модель User."""

    # is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id',
                  'username', 'first_name',
                  'last_name')

    # def get_is_subscribed(self, obj):
    #     """
    #     Метод возвращает False, если юзер не подписан на пользователя
    #     или если запрос сделан неавторизованным юзером, True - если
    #     объект подписки существует.
    #     """
    #     user = self.context['request'].user
    #     if user.is_anonymous:
    #         return False
    #     return user.follower.filter(author=obj).exists()

# class RecipeSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Recipe
#         fields = ('author', 'tag')
