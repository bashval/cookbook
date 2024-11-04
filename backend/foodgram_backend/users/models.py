from django.contrib.auth.models import AbstractUser
from django.db import models

from .constants import EMAIL_LENGTH, NAME_LENGTH


class Users(AbstractUser):
    avatar = models.ImageField(
        'Аватар', upload_to='/users/avatars/', null=True, default=None)
    first_name = models.CharField(
        'Имя', max_length=NAME_LENGTH, blank=False)
    last_name = models.CharField(
        'Фамилия', max_length=NAME_LENGTH, blank=False)
    email = models.EmailField(
        'Адрес электронной почты', max_length=EMAIL_LENGTH, unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ['id']


class Follow(models.Model):
    user = models.ForeignKey(
        Users, on_delete=models.CASCADE, related_name='following'
    )
    following = models.ForeignKey(
        Users, on_delete=models.CASCADE, related_name='followers'
    )

    class Meta:
        verbose_name = 'подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'], name='unique_followers'
            )
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.following}'
