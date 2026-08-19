"""Tests for the seed recipe builder and idempotent seeding."""
import pytest
from mongomock_motor import AsyncMongoMockClient

from app.adapters.db.mongo_recipe_repo import MongoRecipeRepo
from app.seed import (
    build_dierbroodjes,
    build_salade_garnalen,
    build_salade_kip_pesto,
    build_seed_recipe,
    build_spaghetti_bolognese,
    seed_missing,
    seed_recipes,
)


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


def test_all_seed_recipes_are_valid_and_uniquely_ided():
    recipes = seed_recipes()
    assert len(recipes) == 5
    ids = [r.id for r in recipes]
    assert len(set(ids)) == 5  # no duplicate ids
    for recipe in recipes:
        assert recipe.title
        assert recipe.icon
        assert recipe.servings >= 1
        assert recipe.steps  # every recipe has steps
        assert recipe.ingredients


def test_new_recipe_builders_core_facts():
    bolo = build_spaghetti_bolognese()
    assert bolo.id == "spaghetti-bolognese"
    assert bolo.servings == 2
    by_name = {i.name: i for i in bolo.ingredients}
    assert by_name["rundergehakt"].quantity == 200
    assert by_name["spaghetti"].quantity == 200

    garnalen = build_salade_garnalen()
    assert garnalen.id == "salade-garnalen"
    assert garnalen.icon == "🦐"

    kip = build_salade_kip_pesto()
    assert kip.id == "salade-kip-pesto"
    assert any(i.name == "pesto" for i in kip.ingredients)


def test_dierbroodjes_core_facts():
    recipe = build_dierbroodjes()
    assert recipe.id == "zachte-dierbroodjes"
    assert recipe.category == "bake"
    assert recipe.icon == "🍞"
    assert recipe.servings == 8
    assert len(recipe.steps) >= 10
    phases = {step.phase for step in recipe.steps}
    assert len(phases) >= 2  # steps span multiple phases
    by_name = _ingredients_by_name(recipe)
    assert by_name["broodmeel"].quantity == 310
    assert by_name["broodmeel"].unit == "g"
    groups = {ing.group for ing in recipe.ingredients}
    assert {"Deeg", "Decoratie", "Glans"} <= groups
    # Elaborate, non-summarized steps.
    assert all(len(step.instructions) > 20 for step in recipe.steps)


def test_all_seed_recipes_now_five_unique():
    recipes = seed_recipes()
    assert len(recipes) == 5
    ids = [r.id for r in recipes]
    assert len(set(ids)) == 5
    assert "zachte-dierbroodjes" in ids


@pytest.mark.asyncio
async def test_seed_missing_inserts_all_and_is_idempotent():
    db = AsyncMongoMockClient()["basket_test"]
    repo = MongoRecipeRepo(db)
    assert await repo.count() == 0
    await seed_missing(repo)
    assert await repo.count() == 5
    await seed_missing(repo)  # idempotent — no duplicates
    assert await repo.count() == 5


@pytest.mark.asyncio
async def test_seed_missing_adds_only_new_recipes():
    db = AsyncMongoMockClient()["basket_test"]
    repo = MongoRecipeRepo(db)
    await repo.create(build_seed_recipe())  # macaroni already present
    assert await repo.count() == 1
    await seed_missing(repo)
    assert await repo.count() == 5  # the four new ones got added
