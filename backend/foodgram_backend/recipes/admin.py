from django.contrib import admin

from .models import (
    Ingredient, FavoriteRecipe, Recipe,
    RecipeIngredient, RecipeTag, ShoppingCart, Tag
)


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'measurement_unit')
    search_fields = ('name',)


class IngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


class TagInline(admin.TabularInline):
    model = RecipeTag
    extra = 1


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
