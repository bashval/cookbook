from io import BytesIO

from django.conf import settings
from django.db.models import QuerySet
from django.urls import reverse
from django.utils.crypto import get_random_string
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from .constants import (
    HEADER_FONT_SIZE, LINE_FONT_SIZE, NEW_LINE_OFFSET,
    PAGE_LEFT_MARGIN, PAGE_X_SIZE, PAGE_Y_SIZE, SHORT_LINK_LENGTH)
from .models import ShortLink


def create_short_link(request, pk):
    """Create short link for recipr in request,
    create and return new ShortLink instanse with the short link."""
    while True:
        slug = get_random_string(length=SHORT_LINK_LENGTH)
        if not ShortLink.objects.filter(short_link_slug=slug).exists():
            break

    short_link_url = request.build_absolute_uri(reverse(
        'short_link_redirect',
        kwargs={'slug': slug}
    ))
    redirect_url = (request
                    .build_absolute_uri()
                    .replace('api/', '')
                    .replace('get-link/', ''))

    new_short_link = ShortLink(
        short_link_slug=slug,
        redirect_url=redirect_url,
        short_link_url=short_link_url
    )
    new_short_link.save()
    return new_short_link


def get_ingredients_amount(recipes: QuerySet) -> list:
    """Retrieve ingtedients from queryset of recipes,
    calculates total amount af all ingredients
    and returns a list of ingredients and amounts.
    """
    count = 0
    shoping_list = {}
    for recipe in recipes:
        for ingredient in recipe.ingredients.all():
            ingredient_name = ingredient.__str__()
            count += 1
            ingredient_amount = (
                ingredient.recipeingredient_set.get(recipe=recipe).amount)
            total_amount = shoping_list.setdefault(ingredient_name, 0)
            shoping_list[ingredient_name] = total_amount + ingredient_amount
    return [f'{name} - {amount}' for name, amount in shoping_list.items()]


def print_list_to_pdf(data: list, list_header) -> BytesIO:
    """Returns BinaryI/O object with pdf page of data
    printed in a list line by line with list header on the top.
    """
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=(PAGE_X_SIZE, PAGE_Y_SIZE))
    pdfmetrics.registerFont(TTFont(
        'OpenSans',
        settings.FONTS_DIR / 'OpenSans-Regular.ttf'
    ))
    p.setFont('OpenSans', HEADER_FONT_SIZE)
    p.drawCentredString(
        PAGE_X_SIZE / 2,
        PAGE_Y_SIZE - NEW_LINE_OFFSET * 2,
        list_header)
    p.setFont('OpenSans', LINE_FONT_SIZE)
    for count, row in enumerate(data):
        line = f'{count + 1}. {row}'
        y_position = PAGE_Y_SIZE - (3 + count) * NEW_LINE_OFFSET
        p.drawString(PAGE_LEFT_MARGIN, y_position, line)
    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer


def get_pdf_shopping_list(recipes: QuerySet) -> BytesIO:
    shoping_list = get_ingredients_amount(recipes)
    return print_list_to_pdf(shoping_list, 'Список покупок:')
