from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.filters import CustomSearchFilter, RecipeFilter
from api.paginators import PageLimitPagination
from api.permissions import IsAuthorOrAdminOrReadOnly
from api.serializers import (CartSerializer, FavoriteSerializer,
                             FollowSerializer, IngredientSerializer,
                             RecipeCreateSerializer, RecipeListSerializer,
                             TagSerializer)
from recipes.models import (Cart, Favorite, Ingredient, Recipe,
                            RecipeIngredient, Tag)
from users.models import Follow, User


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Viewset тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Viewset ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (CustomSearchFilter,)
    search_fields = ('^name',)


class FollowViewSet(viewsets.ModelViewSet):
    """Viewset просмотра подписок."""
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated, ]
    pagination_class = PageLimitPagination

    def get_queryset(self):
        return Follow.objects.filter(
            user=self.request.user).prefetch_related('author')


class FollowAPIView(APIView):
    """ApiView для создания и удаления подписок."""
    permission_classes = [IsAuthenticated, ]

    def post(self, request, author_id):
        author = get_object_or_404(User, id=author_id)
        if request.user == author:
            return self.response_error(
                'Вы не можете подписаться на самого себя.'
            )

        if Follow.objects.filter(author=author, user=request.user).exists():
            return self.response_error('Вы уже подписаны на этого автора.')

        follow = Follow.objects.create(author=author, user=request.user)

        serializer = FollowSerializer(follow, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, author_id):
        author = get_object_or_404(User, id=author_id)

        if not Follow.objects.filter(
                author=author, user=request.user).exists():
            return self.response_error('Вы еще не подписаны на этого автора.')

        Follow.objects.filter(author=author, user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def response_error(self, message):
        return Response(
            {'errors': message},
            status=status.HTTP_400_BAD_REQUEST
        )


class RecipeViewSet(viewsets.ModelViewSet):
    """Viewset рецептов."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeListSerializer
    pagination_class = PageLimitPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    permission_classes = (IsAuthorOrAdminOrReadOnly,)

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PUT', 'PATCH']:
            return RecipeCreateSerializer
        return RecipeListSerializer

    def recipe_action(self, request, pk, model, serializer_class):
        recipe = get_object_or_404(Recipe, id=pk)
        user = request.user
        if request.method == 'POST':
            instance, created = model.objects.get_or_create(
                user=user, recipe=recipe
            )
            if created:
                serializer = serializer_class(
                    instance, context={'request': request}
                )
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )

            return Response(
                {'detail': 'Уже существует.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        instance = model.objects.filter(user=user, recipe=recipe)
        if instance.exists():
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(
            {'detail': 'Не существует.'},
            status=status.HTTP_400_BAD_REQUEST
        )

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        url_path='shopping_cart',
        permission_classes=[IsAuthenticated],
    )
    def shopping_cart(self, request, pk=None):
        return self.recipe_action(request, pk, Cart, CartSerializer)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        url_path='favorite',
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, pk=None):
        return self.recipe_action(request, pk, Favorite, FavoriteSerializer)

    @action(
        detail=False,
        methods=['GET'],
        url_path='download_shopping_cart',
        permission_classes=[IsAuthenticated],
    )
    def download_shopping_cart(self, request):
        list_ingredients = (
            RecipeIngredient.objects.filter(
                recipe__cart_recipe__user=request.user)
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(total_amount=Sum('amount'))
        )
        shop_list = ['Список покупок\n\n']
        for ingredient in list_ingredients:
            total_amount = ingredient['total_amount']
            name = ingredient['ingredient__name']
            measurement_unit = ingredient['ingredient__measurement_unit']
            shop_list.append(
                f"{name} - {total_amount} {measurement_unit}\n"
            )

        return HttpResponse(
            shop_list,
            {
                "Content-Type": "text/plain",
                "Content-Disposition": 'attachment; filename="shop_list.txt"',
            },
        )
