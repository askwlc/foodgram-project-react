from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Модель пользователя"""
    first_name = models.CharField(max_length=150, verbose_name='Имя')
    last_name = models.CharField(max_length=150, verbose_name='Фамилия')
    username = models.CharField(max_length=150, unique=True, verbose_name='Имя пользователя')
    email = models.EmailField(max_length=254, unique=True, verbose_name='Email')
    password = models.CharField(max_length=150, verbose_name='Пароль')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return self.username


class Follow(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'user'],
                name='unique_following'
            ),
        ]

    def save(self, *args, **kwargs):
        if self.user == self.author:
            raise ValueError("Нельзя подписываться на себя")
        super().save(*args, **kwargs)
