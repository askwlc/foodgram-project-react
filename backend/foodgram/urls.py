# from django.conf import settings
# from django.conf.urls.static import static
# from django.contrib import admin
# from django.urls import include, path
# from rest_framework.routers import DefaultRouter
#
# # from recipes.views import IngredientViewSet, RecipeViewSet, TagViewSet
# # from users.views import UserViewSet
#
# router = DefaultRouter()
# # router.register(r'recipes', RecipeViewSet)
# # router.register(r'tags', TagViewSet)
# # router.register(r'ingredients', IngredientViewSet)
# router.register('users', UserViewSet, basename='users')
#
#
# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('api/', include(router.urls)),
#     path('api/', include('djoser.urls')),
#     path('api/auth/', include('djoser.urls.authtoken')),
# ]
#
#
# if settings.DEBUG:
#     urlpatterns += static(
#         settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
#     )

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
