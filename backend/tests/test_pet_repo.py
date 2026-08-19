"""Tests for the pet-food domain, Mongo repo adapter and seeding.

These use ``mongomock_motor.AsyncMongoMockClient`` so no real MongoDB is
needed. They exercise the pet-food CRUD round-trip and the idempotent seed.
"""
import pytest
from mongomock_motor import AsyncMongoMockClient

from app.adapters.db.mongo_pet_food_repo import MongoPetFoodRepo
from app.domain.pet import PetFood
from app.seed import PET_FOOD_SEED, seed_pet_foods_if_empty


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
async def test_seed_pet_foods_if_empty_is_idempotent():
    repo = MongoPetFoodRepo(_db())
    await seed_pet_foods_if_empty(repo)
    assert await repo.count() == len(PET_FOOD_SEED)
    await seed_pet_foods_if_empty(repo)  # idempotent — no duplicates
    assert await repo.count() == len(PET_FOOD_SEED)
    names = {f.name for f in await repo.list()}
    assert {"paprika", "komkommer", "ijsbergsla", "wortel",
            "andijvie", "veldsla"} <= names
