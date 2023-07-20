from django_filters.rest_framework import FilterSet, filters

from recipes.models import Recipe, Tag


class RecipeFilter(FilterSet):
    is_favorited = filters.BooleanFilter(
        method='is_favorited_filter')
    is_in_shopping_cart = filters.BooleanFilter(
        method='is_in_shopping_cart_filter')
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author',)

    def is_favorited_filter(self, queryset, name, value):
        return (queryset, queryset.filter(favorite__user=self.request.user))[
            all([value, self.request.user.is_authenticated])
        ]

    def is_in_shopping_cart_filter(self, queryset, name, value):
        return (queryset, queryset.filter(purchase__user=self.request.user))[
            all([value, self.request.user.is_authenticated])
        ]

    def filter_queryset(self, queryset):
        tags = self.request.query_params.getlist('tags')
        shopping_cart = self.request.query_params.getlist(
            'is_in_shopping_cart'
        )
        if (
            not (
                self.request.parser_context.get('kwargs')
                or tags
                or shopping_cart
            )
        ):
            return Recipe.objects.none()
        return super().filter_queryset(queryset)
