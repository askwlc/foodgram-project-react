# from django.contrib.auth import get_user_model
# from django.shortcuts import get_object_or_404
# from rest_framework import viewsets, status, permissions
# from rest_framework.response import Response
# from rest_framework.decorators import action
# from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
# from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
#

#
# User = get_user_model()
#
#
# class UserViewSet(viewsets.ModelViewSet):
#     """Отображение и редактирование модели User."""
#     serializer_class = UserSerializer
#     queryset = User.objects.all()
#
#     def get_permissions(self):
#         """Список разрешений."""
#         if self.action in ['list', 'retrieve']:
#             permission_classes = [permissions.AllowAny]
#         else:
#             permission_classes = [permissions.IsAuthenticated]
#         return [permission() for permission in permission_classes]
#
#     @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
#     def me(self, request):
#         """Создаёт ресурс me, возвращает информацию о пользователе, сделавшего запрос."""
#         serializer = UserSerializer(request.user)
#         return Response(serializer.data)
#
#     @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
#     def set_password(self, request):
#         """Создаёт ресурс set_password для смены пароля текущего пользователя."""
#         serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
#         if serializer.is_valid():
#             request.user.set_password(serializer.validated_data['new_password'])
#             request.user.save()
#             return Response(status=status.HTTP_204_NO_CONTENT)
#         return Response(status=status.HTTP_400_BAD_REQUEST)


# class CustomTokenObtainPairView(TokenObtainPairView):
#     """Получение токенов."""
#     serializer_class = CustomTokenObtainPairSerializer
#
#     def post(self, request, *args, **kwargs):
#         """Переопределение метода для добавления дополнительных проверок."""
#         serializer = self.get_serializer(data=request.data)
#         try:
#             serializer.is_valid(raise_exception=True)
#         except TokenError as e:
#             raise InvalidToken(e.args[0])
#
#         return Response(serializer.validated_data, status=status.HTTP_201_CREATED)
#
#
# class CustomTokenRefreshView(TokenRefreshView):
#     """Обновление токенов."""
#     def post(self, request, *args, **kwargs):
#         """Переопределение метода для добавления дополнительных проверок."""
#         serializer = self.get_serializer(data=request.data)
#         try:
#             serializer.is_valid(raise_exception=True)
#         except TokenError as e:
#             raise InvalidToken(e.args[0])
#
#         return Response(serializer.validated_data, status=status.HTTP_200_OK)


