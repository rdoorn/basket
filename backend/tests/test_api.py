"""Integration tests for the REST API.

These drive the ASGI app directly via httpx ``ASGITransport`` with the repo
dependencies overridden to point at an in-memory ``mongomock_motor`` database,
so no real MongoDB (or network) is needed.
"""
from datetime import date, timedelta

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from mongomock_motor import AsyncMongoMockClient

from app.adapters.db.mongo_menu_repo import MongoMenuRepo
from app.adapters.db.mongo_recipe_repo import MongoRecipeRepo
from app.api.deps import get_menu_repo, get_recipe_repo
from app.main import app
from app.seed import seed_if_empty


@pytest_asyncio.fixture
async def client():
    """Yield an AsyncClient wired to a fresh mongomock-backed app."""
    db = AsyncMongoMockClient()["basket_test"]
    recipe_repo = MongoRecipeRepo(db)
    menu_repo = MongoMenuRepo(db)
    await seed_if_empty(recipe_repo)

    app.dependency_overrides[get_recipe_repo] = lambda: recipe_repo
    app.dependency_overrides[get_menu_repo] = lambda: menu_repo

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


def _today() -> str:
    return date.today().isoformat()


def _plus(days: int) -> str:
    return (date.today() + timedelta(days=days)).isoformat()


@pytest.mark.asyncio
async def test_list_recipes_returns_seed_card(client):
    resp = await client.get("/recipes")
    assert resp.status_code == 200
    cards = resp.json()
    assert len(cards) == 1
    card = cards[0]
    assert card["id"] == "macaroni-alla-siciliana"
    assert card["icon"] == "🍝"
    assert "Siciliana" in card["title"]


@pytest.mark.asyncio
async def test_get_recipe_full(client):
    resp = await client.get("/recipes/macaroni-alla-siciliana")
    assert resp.status_code == 200
    body = resp.json()
    assert body["servings"] == 4
    assert len(body["steps"]) >= 9
    assert body["ingredients"][0]["name"] == "macaroni"


@pytest.mark.asyncio
async def test_get_recipe_missing_404(client):
    resp = await client.get("/recipes/nope")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_create_update_delete_recipe(client):
    new_recipe = {
        "title": "Nieuw",
        "icon": "🥗",
        "description": "d",
        "servings": 2,
        "total_time_min_low": 10,
        "total_time_min_high": 15,
        "tags": [],
        "notes": None,
        "ingredients": [{"name": "sla", "quantity": 1, "unit": "krop"}],
        "steps": [],
    }
    created = await client.post("/recipes", json=new_recipe)
    assert created.status_code == 201
    rid = created.json()["id"]
    assert rid

    fetched = await client.get(f"/recipes/{rid}")
    assert fetched.status_code == 200
    assert fetched.json()["title"] == "Nieuw"

    updated = dict(new_recipe)
    updated["title"] = "Aangepast"
    put = await client.put(f"/recipes/{rid}", json=updated)
    assert put.status_code == 200
    assert put.json()["title"] == "Aangepast"

    deleted = await client.delete(f"/recipes/{rid}")
    assert deleted.status_code in (200, 204)
    assert (await client.get(f"/recipes/{rid}")).status_code == 404


@pytest.mark.asyncio
async def test_update_missing_recipe_404(client):
    put = await client.put(
        "/recipes/nope",
        json={
            "title": "x", "icon": "x", "description": "", "servings": 1,
            "total_time_min_low": None, "total_time_min_high": None,
            "tags": [], "notes": None, "ingredients": [], "steps": [],
        },
    )
    assert put.status_code == 404


@pytest.mark.asyncio
async def test_weekmenu_returns_14_day_window(client):
    resp = await client.get("/weekmenu")
    assert resp.status_code == 200
    days = resp.json()["days"]
    assert len(days) == 14
    assert days[0]["date"] == _today()
    assert days[13]["date"] == _plus(13)
    assert all(day["assignment"] is None for day in days)


@pytest.mark.asyncio
async def test_assign_then_move_swaps(client):
    rid = "macaroni-alla-siciliana"
    # Assign to today.
    r1 = await client.put(
        "/weekmenu/assignments",
        json={"date": _today(), "recipeId": rid, "multiplier": 1.0},
    )
    assert r1.status_code == 200

    # Assign a second (same recipe) to tomorrow with 2x.
    await client.put(
        "/weekmenu/assignments",
        json={"date": _plus(1), "recipeId": rid, "multiplier": 2.0},
    )

    # Move today onto tomorrow -> swap.
    swap = await client.put(
        "/weekmenu/assignments",
        json={
            "date": _plus(1),
            "recipeId": rid,
            "multiplier": 1.0,
            "fromDate": _today(),
        },
    )
    assert swap.status_code == 200
    assignments = swap.json()["assignments"]
    # today now holds the former tomorrow assignment (2x), tomorrow holds 1x.
    assert assignments[_today()]["multiplier"] == 2.0
    assert assignments[_plus(1)]["multiplier"] == 1.0


@pytest.mark.asyncio
async def test_delete_assignment_clears_day(client):
    rid = "macaroni-alla-siciliana"
    await client.put(
        "/weekmenu/assignments",
        json={"date": _today(), "recipeId": rid, "multiplier": 1.0},
    )
    resp = await client.delete(f"/weekmenu/assignments/{_today()}")
    assert resp.status_code == 200
    assert resp.json()["assignments"] == {}


@pytest.mark.asyncio
async def test_shopping_list_scales_by_multiplier(client):
    rid = "macaroni-alla-siciliana"
    await client.put(
        "/weekmenu/assignments",
        json={"date": _today(), "recipeId": rid, "multiplier": 2.0},
    )
    resp = await client.get("/shopping-list")
    assert resp.status_code == 200
    items = resp.json()["items"]
    by_name = {i["name"]: i for i in items}
    assert by_name["macaroni"]["quantity"] == 700


@pytest.mark.asyncio
async def test_pricing_quote_two_stores_with_totals(client):
    rid = "macaroni-alla-siciliana"
    await client.put(
        "/weekmenu/assignments",
        json={"date": _today(), "recipeId": rid, "multiplier": 1.0},
    )
    resp = await client.post("/pricing/quote")
    assert resp.status_code == 200
    quotes = resp.json()["quotes"]
    stores = {q["store"] for q in quotes}
    assert stores == {"Albert Heijn", "Picnic"}
    for q in quotes:
        assert q["total"] == pytest.approx(sum(i["line_total"] for i in q["items"]))
    # external-source gehakt is excluded from store pricing
    for q in quotes:
        assert all(i["name"] != "gehakt" for i in q["items"])
