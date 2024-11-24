from django.shortcuts import get_object_or_404, redirect

from .models import ShortLink


def short_link_redirect(request, slug):
    link = get_object_or_404(ShortLink, short_link_slug=slug)
    return redirect(link.redirect_url)
