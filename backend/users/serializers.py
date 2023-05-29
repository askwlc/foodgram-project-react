from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Обрабатывает модель User."""

    class Meta:
        model = User
        fields = ['email', 'id', 'username', 'first_name', 'last_name']
        read_only_fields = ['id']


class ChangePasswordSerializer(serializers.Serializer):
    """Обрабатывает изменение пароля пользователя."""
    new_password = serializers.CharField(required=True)
    current_password = serializers.CharField(required=True)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Обрабатывает создание токенов JWT."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        return token
