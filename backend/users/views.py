from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .serializers import UserSerializer, ChangePasswordSerializer, CustomTokenObtainPairSerializer


class UserViewSet:
    pass


class CustomTokenObtainPairView:
    pass


class CustomTokenRefreshView:
    pass