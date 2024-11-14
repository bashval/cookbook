from django.contrib.auth.models import AbstractUser
from django.db import models

from .constants import EMAIL_LENGTH, NAME_LENGTH


class User(AbstractUser):
    avatar = models.ImageField(
        'Аватар', upload_to='users/', null=True, default=None)
    first_name = models.CharField(
        'Имя', max_length=NAME_LENGTH, blank=False)
    last_name = models.CharField(
        'Фамилия', max_length=NAME_LENGTH, blank=False)
    email = models.EmailField(
        'Адрес электронной почты', max_length=EMAIL_LENGTH, unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['id']

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Subscription(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='subscriptions'
    )
    subscribing = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers',
        related_query_name='subscribing'
    )

    class Meta:
        verbose_name = 'подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'subscribing'], name='unique_followers'
            )
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.subscribing}'
