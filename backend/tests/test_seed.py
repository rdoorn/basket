"""Tests for the seed recipe builder and idempotent seeding."""
import pytest
from mongomock_motor import AsyncMongoMockClient

from app.adapters.db.mongo_recipe_repo import MongoRecipeRepo
from app.seed import build_seed_recipe, seed_if_empty


def _ingredients_by_name(recipe):
    """Return a name -> Ingredient map for the recipe."""
    return {ing.name: ing for ing in recipe.ingredients}


def test_seed_recipe_core_metadata():
    recipe = build_seed_recipe()
    assert recipe.servings == 4
    assert recipe.icon == "🍝"
    assert recipe.total_time_min_low == 50
    assert recipe.total_time_min_high == 60
    assert "Siciliana" in recipe.title
    assert recipe.notes == "Gehakt zonder zout."


def test_seed_recipe_has_at_least_nine_steps_and_a_prep_step():
    recipe = build_seed_recipe()
    assert len(recipe.steps) >= 9
    phases = {step.phase for step in recipe.steps}
    assert "prep" in phases
    assert "cook" in phases
    assert "finish" in phases


def test_seed_recipe_steps_have_full_instructions():
    recipe = build_seed_recipe()
    # Instructions preserve elaborate reasoning, not one-liners.
    assert all(len(step.instructions) > 20 for step in recipe.steps)


def test_seed_recipe_key_ingredients():
    recipe = build_seed_recipe()
    by_name = _ingredients_by_name(recipe)
    assert by_name["macaroni"].quantity == 350
    assert by_name["macaroni"].unit == "g"
    assert by_name["gehakt"].quantity == 300
    assert by_name["gehakt"].unit == "g"


def test_seed_recipe_has_expected_groups():
    recipe = build_seed_recipe()
    groups = {ing.group for ing in recipe.ingredients}
    assert {"Pasta", "Basis", "Tomatenbasis", "Kruiden", "Frisse afwerking"} <= groups


@pytest.mark.asyncio
async def test_seed_if_empty_inserts_once_and_is_idempotent():
    db = AsyncMongoMockClient()["basket_test"]
    repo = MongoRecipeRepo(db)
    assert await repo.count() == 0
    await seed_if_empty(repo)
    assert await repo.count() == 1
    await seed_if_empty(repo)
    assert await repo.count() == 1
