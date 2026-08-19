"""Tests for the pet-food domain, Mongo repo adapter and seeding.

These use ``mongomock_motor.AsyncMongoMockClient`` so no real MongoDB is
needed. They exercise the pet-food CRUD round-trip and the idempotent seed.
"""
import pytest
from mongomock_motor import AsyncMongoMockClient

from app.adapters.db.mongo_pet_food_repo import MongoPetFoodRepo
from app.domain.pet import PetFood
from app.seed import PET_FOOD_SEED, seed_pet_foods_missing


def _db():
    """Return a fresh in-memory mongomock database."""
    return AsyncMongoMockClient()["basket_test"]


@pytest.mark.asyncio
async def test_pet_food_create_assigns_id_and_round_trips():
    repo = MongoPetFoodRepo(_db())
    created = await repo.create(PetFood(id="", name="paprika", weight_g=150))
    assert created.id
    listed = await repo.list()
    assert len(listed) == 1
    assert listed[0].name == "paprika"
    assert listed[0].weight_g == 150


@pytest.mark.asyncio
async def test_pet_food_delete_removes():
    repo = MongoPetFoodRepo(_db())
    created = await repo.create(PetFood(id="", name="wortel", weight_g=80))
    assert await repo.delete(created.id) is True
    assert await repo.list() == []
    assert await repo.delete(created.id) is False


@pytest.mark.asyncio
async def test_pet_food_count():
    repo = MongoPetFoodRepo(_db())
    assert await repo.count() == 0
    await repo.create(PetFood(id="", name="komkommer", weight_g=400))
    assert await repo.count() == 1


@pytest.mark.asyncio
async def test_seed_pet_foods_missing_is_idempotent():
    repo = MongoPetFoodRepo(_db())
    await seed_pet_foods_missing(repo)
    assert await repo.count() == len(PET_FOOD_SEED)
    await seed_pet_foods_missing(repo)  # idempotent — no duplicates
    assert await repo.count() == len(PET_FOOD_SEED)
    names = {f.name for f in await repo.list()}
    assert {"paprika", "komkommer", "ijsbergsla", "wortel", "andijvie",
            "veldsla", "koolrabi", "mais (vers)", "witlof",
            "babyromaine"} <= names


@pytest.mark.asyncio
async def test_seed_pet_foods_missing_adds_only_new_foods():
    # A pre-existing collection (missing the newer starter foods) gains only the
    # foods it lacks, and a user's own addition is preserved.
    repo = MongoPetFoodRepo(_db())
    await repo.create(PetFood(id="", name="paprika", weight_g=150))
    await repo.create(PetFood(id="", name="eigen-groente", weight_g=99))
    await seed_pet_foods_missing(repo)
    names = {f.name for f in await repo.list()}
    assert "koolrabi" in names          # new starter food added
    assert "eigen-groente" in names     # user's own food preserved
    # paprika not duplicated
    assert sum(1 for f in await repo.list() if f.name == "paprika") == 1
