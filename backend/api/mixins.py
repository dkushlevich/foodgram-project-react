from recipes.models import Recipe


class ShortRecipeRepresentationMixin:

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.pop('user')
        recipe = Recipe.objects.get(pk=representation.pop('recipe'))
        representation['id'] = recipe.id
        representation['name'] = recipe.name
        representation['image'] = self.context['request'].build_absolute_uri(
            recipe.image.url
        )
        representation['cooking_time'] = recipe.cooking_time
        return representation
