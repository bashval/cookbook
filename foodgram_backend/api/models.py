from django.db import models

from .constants import SHORT_LINK_LENGTH


class ShortLink(models.Model):
    short_link_slug = models.CharField(
        'Слаг короткой ссылки', max_length=SHORT_LINK_LENGTH, unique=True)
    redirect_url = models.URLField(
        'Оригинальная ссылка', null=True, blank=True)
    short_link_url = models.URLField(
        'Короткая ссылка', null=True, blank=True)

    class Meta:
        verbose_name = 'короткая ссылка'
        verbose_name_plural = 'Короткие ссылки'

    def __str__(self):
        return (f'{self.short_link_slug} - слаг '
                f'ссылки на адрес {self.redirect_url}')
