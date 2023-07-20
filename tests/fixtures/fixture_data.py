import os
from io import BytesIO
import shutil

import pytest
from PIL import Image

from recipes.models import (
    Favorite, Ingredient, IngredientRecipe, Purchase,
    Recipe, Tag, Unit
)
from users.models import Subscription
from tests.conftest import BASE_DIR


@pytest.fixture
def tag_1():
    return Tag.objects.create(
        name='TestTag1',
        slug='TestTagSlug2',
        color='#b03f95'
    )


@pytest.fixture
def tag_2():
    return Tag.objects.create(
        name='TestTag2',
        slug='TestTagSlug2',
        color='#b03f96'
    )


@pytest.fixture
def unit():
    return Unit.objects.create(
        name='UnitName'
    )


@pytest.fixture
def ingredient_1(unit):
    return Ingredient.objects.create(
        name='IngredientName1',
        measurement_unit=unit,
    )


@pytest.fixture
def ingredient_2(unit):
    return Ingredient.objects.create(
        name='IngredientName2',
        measurement_unit=unit,
    )


@pytest.fixture
def recipe_1(user, tag_1):
    recipe = Recipe.objects.create(
        name='TestRecipe',
        text='TextTestRecipe',
        cooking_time=150,
        author=user,
    )
    image_path = os.path.join(BASE_DIR, 'tests/img/test.png')
    with open(image_path, 'rb') as f:
        image_data = f.read()
        image = Image.open(BytesIO(image_data))
        recipe.image.save('test.png', BytesIO(image.tobytes()))
    recipe.tags.set([tag_1])
    return recipe


@pytest.fixture
def recipe_2(user, tag_1, tag_2):
    recipe = Recipe.objects.create(
        name='TestRecipe',
        text='TextTestRecipe',
        cooking_time=150,
        author=user,
    )
    image_path = os.path.join(BASE_DIR, 'tests/img/test.png')
    with open(image_path, 'rb') as file:
        image_data = file.read()
        image = Image.open(BytesIO(image_data))
        recipe.image.save('test.png', BytesIO(image.tobytes()))
    recipe.tags.set([tag_1, tag_2])
    return recipe


@pytest.fixture
def ingredientrecipe_1(recipe_1, ingredient_1):
    return IngredientRecipe.objects.create(
        recipe=recipe_1,
        ingredient=ingredient_1,
        amount=10
    )


@pytest.fixture
def favorite(recipe_1, user):
    return Favorite.objects.create(
        recipe=recipe_1,
        user=user
    )


@pytest.fixture
def purchase(recipe_1, user):
    return Purchase.objects.create(
        recipe=recipe_1,
        user=user
    )


@pytest.fixture
def subscription_1(user, another_user):
    return Subscription.objects.create(
        user=user,
        author=another_user
    )


@pytest.fixture(autouse=True)
def media_cleanup(request, settings):
    yield
    try:
        shutil.rmtree(settings.MEDIA_ROOT)
    except Exception:
        pass
