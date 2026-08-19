"""Tests for the staple domain, Mongo repo adapter and seeding.

These use ``mongomock_motor.AsyncMongoMockClient`` so no real MongoDB is
needed. They exercise the staple CRUD round-trip and the idempotent seed.
"""
import pytest
from mongomock_motor import AsyncMongoMockClient

from app.adapters.db.mongo_staple_repo import MongoStapleRepo
from app.domain.staple import Staple
from app.seed import STAPLE_SEED, seed_staples_if_empty


def _db():
    """Return a fresh in-memory mongomock database."""
    return AsyncMongoMockClient()["basket_test"]


@pytest.mark.asyncio
async def test_staple_create_assigns_id_and_stores_normalized():
    repo = MongoStapleRepo(_db())
    created = await repo.create(Staple(id="", name="Suiker"))
    assert created.id
    assert created.name == "suiker"  # stored normalized
    listed = await repo.list()
    assert len(listed) == 1
    assert listed[0].name == "suiker"


@pytest.mark.asyncio
async def test_staple_delete_removes():
    repo = MongoStapleRepo(_db())
    created = await repo.create(Staple(id="", name="zout"))
    assert await repo.delete(created.id) is True
    assert await repo.list() == []
    assert await repo.delete(created.id) is False


@pytest.mark.asyncio
async def test_staple_count():
    repo = MongoStapleRepo(_db())
    assert await repo.count() == 0
    await repo.create(Staple(id="", name="olijfolie"))
    assert await repo.count() == 1


@pytest.mark.asyncio
async def test_seed_staples_if_empty_is_idempotent():
    repo = MongoStapleRepo(_db())
    await seed_staples_if_empty(repo)
    assert await repo.count() == len(STAPLE_SEED)
    await seed_staples_if_empty(repo)  # idempotent — no duplicates
    assert await repo.count() == len(STAPLE_SEED)
    names = {s.name for s in await repo.list()}
    # legacy defaults plus the new bake staples
    assert {"olijfolie", "citroensap", "chilivlokken", "gehakt",
            "rundergehakt", "zout", "zwarte peper", "venkelzaad",
            "suiker", "zwarte sesam", "instant gist",
            "basterdsuiker"} <= names
