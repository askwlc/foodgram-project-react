from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Модель пользователя"""
    first_name = models.CharField(
        max_length=settings.USER_MAX_LENGTH, verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=settings.USER_MAX_LENGTH, verbose_name='Фамилия'
    )
    username = models.CharField(
        max_length=settings.USER_MAX_LENGTH, unique=True,
        verbose_name='Имя пользователя'
    )
    email = models.EmailField(
        max_length=settings.EMAIL_MAX_LENGTH, unique=True,
        verbose_name='Email'
    )
    password = models.CharField(
        max_length=settings.USER_MAX_LENGTH, verbose_name='Пароль'
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Follow(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='author'
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='follower'
    )

    class Meta:
        ordering = ('-author_id',)
        verbose_name = 'Подписки'
        verbose_name_plural = 'Подписки'
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

    def __str__(self):
        return f'{self.user.username} подписан на {self.author.username}'
