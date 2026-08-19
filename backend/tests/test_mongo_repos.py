"""Tests for the Motor-based Mongo repository adapters.

These use ``mongomock_motor.AsyncMongoMockClient`` so no real MongoDB is
needed. They exercise the recipe CRUD round-trip and the week-menu
save/load upsert semantics.
"""
import pytest
from mongomock_motor import AsyncMongoMockClient

from app.adapters.db.mongo_menu_repo import MongoMenuRepo
from app.adapters.db.mongo_recipe_repo import MongoRecipeRepo
from app.domain.menu import DayAssignment, WeekMenu
from app.domain.recipe import Ingredient, Recipe, Step


def _db():
    """Return a fresh in-memory mongomock database."""
    return AsyncMongoMockClient()["basket_test"]


def _recipe(recipe_id: str = "r1") -> Recipe:
    """Return a minimal but complete recipe for round-trip tests."""
    return Recipe(
        id=recipe_id,
        title="Test",
        icon="🍝",
        description="desc",
        servings=4,
        total_time_min_low=50,
        total_time_min_high=60,
        tags=["pasta"],
        notes="n",
        ingredients=[Ingredient(group="Pasta", name="macaroni", quantity=350, unit="g")],
        steps=[
            Step(
                order=1,
                title="Koken",
                phase="cook",
                duration_min_low=8,
                duration_min_high=10,
                instructions="Kook de pasta.",
            )
        ],
    )


@pytest.mark.asyncio
async def test_recipe_create_get_round_trip():
    repo = MongoRecipeRepo(_db())
    created = await repo.create(_recipe())
    assert created.id == "r1"
    fetched = await repo.get("r1")
    assert fetched == _recipe()


@pytest.mark.asyncio
async def test_recipe_create_assigns_id_when_absent():
    repo = MongoRecipeRepo(_db())
    recipe = _recipe(recipe_id="")
    created = await repo.create(recipe)
    assert created.id
    assert await repo.get(created.id) is not None


@pytest.mark.asyncio
async def test_recipe_get_missing_returns_none():
    repo = MongoRecipeRepo(_db())
    assert await repo.get("nope") is None


@pytest.mark.asyncio
async def test_recipe_list_returns_all():
    repo = MongoRecipeRepo(_db())
    await repo.create(_recipe("a"))
    await repo.create(_recipe("b"))
    ids = {r.id for r in await repo.list()}
    assert ids == {"a", "b"}


@pytest.mark.asyncio
async def test_recipe_update_and_delete():
    repo = MongoRecipeRepo(_db())
    await repo.create(_recipe())
    updated = _recipe()
    updated.title = "Changed"
    result = await repo.update("r1", updated)
    assert result is not None
    assert result.title == "Changed"
    assert (await repo.get("r1")).title == "Changed"
    assert await repo.delete("r1") is True
    assert await repo.get("r1") is None
    assert await repo.delete("r1") is False


@pytest.mark.asyncio
async def test_recipe_update_missing_returns_none():
    repo = MongoRecipeRepo(_db())
    assert await repo.update("nope", _recipe("nope")) is None


@pytest.mark.asyncio
async def test_recipe_count():
    repo = MongoRecipeRepo(_db())
    assert await repo.count() == 0
    await repo.create(_recipe())
    assert await repo.count() == 1


@pytest.mark.asyncio
async def test_menu_load_absent_returns_empty():
    repo = MongoMenuRepo(_db())
    menu = await repo.load()
    assert isinstance(menu, WeekMenu)
    assert menu.assignments == {}


@pytest.mark.asyncio
async def test_menu_save_and_load_round_trip():
    repo = MongoMenuRepo(_db())
    menu = WeekMenu()
    menu.set("2026-08-17", DayAssignment(recipe_id="r1", multiplier=2.0))
    await repo.save(menu)
    loaded = await repo.load()
    assert loaded.get("2026-08-17").recipe_id == "r1"
    assert loaded.get("2026-08-17").multiplier == 2.0


@pytest.mark.asyncio
async def test_menu_round_trips_item_choices():
    repo = MongoMenuRepo(_db())
    menu = WeekMenu()
    menu.set("2026-08-17", DayAssignment(recipe_id="r1", multiplier=1.0))
    menu.set_item_buy("gehakt", True)
    menu.set_item_buy("rode paprika", False)
    await repo.save(menu)
    loaded = await repo.load()
    assert loaded.item_choices == {"gehakt": True, "rode paprika": False}


@pytest.mark.asyncio
async def test_menu_round_trips_extras_and_pet_fields():
    repo = MongoMenuRepo(_db())
    menu = WeekMenu()
    menu.set_extra("zachte-dierbroodjes", 2.0)
    menu.pet_target_g = 1250
    menu.pet_selection = ["paprika"]
    await repo.save(menu)
    loaded = await repo.load()
    assert loaded.extras[0].recipe_id == "zachte-dierbroodjes"
    assert loaded.extras[0].multiplier == 2.0
    assert loaded.pet_target_g == 1250
    assert loaded.pet_selection == ["paprika"]


@pytest.mark.asyncio
async def test_menu_load_absent_defaults_pet_fields():
    repo = MongoMenuRepo(_db())
    menu = await repo.load()
    assert menu.extras == []
    assert menu.pet_target_g == 1000
    assert menu.pet_selection == []


@pytest.mark.asyncio
async def test_menu_save_upserts_single_document():
    db = _db()
    repo = MongoMenuRepo(db)
    first = WeekMenu()
    first.set("2026-08-17", DayAssignment(recipe_id="r1"))
    await repo.save(first)
    second = WeekMenu()
    second.set("2026-08-18", DayAssignment(recipe_id="r2"))
    await repo.save(second)
    assert await db["weekmenu"].count_documents({}) == 1
    loaded = await repo.load()
    assert loaded.get("2026-08-17") is None
    assert loaded.get("2026-08-18").recipe_id == "r2"
