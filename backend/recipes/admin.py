from django.contrib import admin
from django.forms.models import BaseInlineFormSet
from django.core.exceptions import ValidationError

from .models import (FavoriteRecipe, Ingredient, Recipe,
                     RecipeIngredient, RecipeTag, ShoppingCart, Tag)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'measurement_unit')
    search_fields = ('name',)


class InlineFormSet(BaseInlineFormSet):
    def clean(self):
        super(InlineFormSet, self).clean()
        create = self.save(commit=False)
        if (len(self.get_queryset()) == len(self.deleted_objects)
                and not create):
            raise ValidationError('Должен остаться хотябы один объект.')


class IngredientInline(admin.TabularInline):
    model = RecipeIngredient
    formset = InlineFormSet
    extra = 0
    min_num = 1


class TagInline(admin.TabularInline):
    model = RecipeTag
    formset = InlineFormSet
    extra = 0
    min_num = 1


class RecipeAdmin(admin.ModelAdmin):
    readonly_fields = ('favorite_count',)
    list_display = ('name', 'author')
    list_display_links = ('name', 'author')
    list_select_related = ('author',)
    search_fields = ('name', 'author__first_name', 'author__last_name')
    list_filter = ('tags',)
    inlines = (IngredientInline, TagInline)

    @admin.display(description='Количество добавлений в избраное')
    def favorite_count(self, obj):
        return obj.is_favorited.count()


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(FavoriteRecipe)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(ShoppingCart)
admin.site.register(Tag, TagAdmin)
