from rest_framework import viewsets
from .models import Recipe, Tag
from api.serializers import RecipeSerializer, TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """Viewset отображения рецептов"""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Viewset отображения тегов"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer