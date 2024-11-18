from io import BytesIO

from django.db.models import QuerySet
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from .constants import (
    HEADER_FONT_SIZE, LINE_FONT_SIZE, NEW_LINE_OFFSET,
    PAGE_LEFT_MARGIN, PAGE_X_SIZE, PAGE_Y_SIZE)


def get_ingredients_amount(recipes: QuerySet) -> list:
    """Retrieve ingtedients from queryset of recipes,
    calculates total amount af all ingredients
    and returns a list of ingredients and amounts.
    """
    shoping_list = {}
    for recipe in recipes:
        for ingredient in recipe.ingredients.all():
            ingredient_name = ingredient.__str__()
            ingredient_amount = int(
                ingredient.recipeingredient_set.first().amount)
            total_amount = shoping_list.setdefault(ingredient_name, 0)
            shoping_list[ingredient_name] = total_amount + ingredient_amount
    return [f'{name} - {amount}' for name, amount in shoping_list.items()]


def print_list_to_pdf(data: list, list_header) -> BytesIO:
    """Returns BinaryI/O object with pdf page of data
    printed in a list line by line with list header on the top.
    """
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=(PAGE_X_SIZE, PAGE_Y_SIZE))
    pdfmetrics.registerFont(TTFont('OpenSans', 'OpenSans-Regular.ttf'))
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
