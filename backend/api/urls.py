from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import (FollowAPIView, FollowViewSet, IngredientViewSet,
                       RecipeViewSet, TagViewSet)

router = DefaultRouter()
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'recipes', RecipeViewSet, basename='recipe')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register('users/subscriptions', FollowViewSet, basename='subscriptions')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('users/<int:author_id>/subscribe/', FollowAPIView.as_view(), name='subscribe')
]
