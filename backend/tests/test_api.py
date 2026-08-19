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
from app.adapters.db.mongo_pet_food_repo import MongoPetFoodRepo
from app.adapters.db.mongo_recipe_repo import MongoRecipeRepo
from app.adapters.db.mongo_staple_repo import MongoStapleRepo
from app.api.deps import (
    get_menu_repo,
    get_pet_food_repo,
    get_recipe_repo,
    get_staple_repo,
)
from app.main import app
from app.seed import (
    seed_missing,
    seed_pet_foods_missing,
    seed_staples_if_empty,
)


@pytest_asyncio.fixture
async def client():
    """Yield an AsyncClient wired to a fresh mongomock-backed app."""
    db = AsyncMongoMockClient()["basket_test"]
    recipe_repo = MongoRecipeRepo(db)
    menu_repo = MongoMenuRepo(db)
    pet_food_repo = MongoPetFoodRepo(db)
    staple_repo = MongoStapleRepo(db)
    await seed_missing(recipe_repo)
    await seed_pet_foods_missing(pet_food_repo)
    await seed_staples_if_empty(staple_repo)

    app.dependency_overrides[get_recipe_repo] = lambda: recipe_repo
    app.dependency_overrides[get_menu_repo] = lambda: menu_repo
    app.dependency_overrides[get_pet_food_repo] = lambda: pet_food_repo
    app.dependency_overrides[get_staple_repo] = lambda: staple_repo

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
    assert len(cards) == 5
    by_id = {c["id"]: c for c in cards}
    assert "macaroni-alla-siciliana" in by_id
    assert "spaghetti-bolognese" in by_id
    assert by_id["macaroni-alla-siciliana"]["icon"] == "🍝"
    assert by_id["macaroni-alla-siciliana"]["category"] == "meal"
    assert by_id["zachte-dierbroodjes"]["category"] == "bake"


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
async def test_extras_add_and_remove(client):
    rid = "macaroni-alla-siciliana"
    r = await client.put(
        "/weekmenu/extras", json={"recipeId": rid, "multiplier": 2.0}
    )
    assert r.status_code == 200
    assert any(
        e["recipeId"] == rid and e["multiplier"] == 2.0
        for e in r.json()["extras"]
    )
    got = await client.get("/weekmenu")
    assert any(e["recipeId"] == rid for e in got.json()["extras"])
    d = await client.delete(f"/weekmenu/extras/{rid}")
    assert all(e["recipeId"] != rid for e in d.json()["extras"])


@pytest.mark.asyncio
async def test_extras_fold_into_shopping_list(client):
    rid = "macaroni-alla-siciliana"
    await client.put(
        "/weekmenu/extras", json={"recipeId": rid, "multiplier": 2.0}
    )
    resp = await client.get("/shopping-list")
    items = {i["name"]: i for i in resp.json()["items"]}
    assert items["macaroni"]["quantity"] == 700


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
    # gehakt is a "heb ik vast wel" staple, so it is not priced until promoted
    for q in quotes:
        assert all(i["name"] != "gehakt" for i in q["items"])


@pytest.mark.asyncio
async def test_shopping_list_splits_staples_into_pantry(client):
    rid = "macaroni-alla-siciliana"
    await client.put(
        "/weekmenu/assignments",
        json={"date": _today(), "recipeId": rid, "multiplier": 1.0},
    )
    resp = await client.get("/shopping-list")
    assert resp.status_code == 200
    body = resp.json()
    items = {i["name"] for i in body["items"]}
    pantry = {i["name"] for i in body["pantry"]}
    # staples land in the pantry, everything else in the shopping list
    assert {"gehakt", "olijfolie", "citroensap", "zout", "zwarte peper"} <= pantry
    assert "macaroni" in items
    assert "citroenrasp" in items  # only citroensap is a staple, not the rasp
    assert items.isdisjoint(pantry)


@pytest.mark.asyncio
async def test_promote_and_unpromote_staple(client):
    rid = "macaroni-alla-siciliana"
    await client.put(
        "/weekmenu/assignments",
        json={"date": _today(), "recipeId": rid, "multiplier": 1.0},
    )
    # Promote gehakt into the shopping list.
    promoted = await client.put(
        "/shopping-list/item", json={"name": "gehakt", "buy": True}
    )
    assert promoted.status_code == 200
    body = promoted.json()
    gehakt = next(i for i in body["items"] if i["name"] == "gehakt")
    assert gehakt["staple"] is True
    assert all(i["name"] != "gehakt" for i in body["pantry"])

    # It now counts toward pricing.
    quotes = (await client.post("/pricing/quote")).json()["quotes"]
    assert any(
        any(i["name"] == "gehakt" for i in q["items"]) for q in quotes
    )

    # Persisted across a fresh GET, and reversible.
    after_get = (await client.get("/shopping-list")).json()
    assert any(i["name"] == "gehakt" for i in after_get["items"])
    reverted = await client.put(
        "/shopping-list/item", json={"name": "gehakt", "buy": False}
    )
    body2 = reverted.json()
    assert any(i["name"] == "gehakt" for i in body2["pantry"])
    assert all(i["name"] != "gehakt" for i in body2["items"])


@pytest.mark.asyncio
async def test_non_staple_can_be_moved_to_pantry_and_back(client):
    rid = "macaroni-alla-siciliana"
    await client.put(
        "/weekmenu/assignments",
        json={"date": _today(), "recipeId": rid, "multiplier": 1.0},
    )
    # Move a normal shopping item (rode paprika) to "heb ik vast wel".
    moved = await client.put(
        "/shopping-list/item", json={"name": "rode paprika", "buy": False}
    )
    body = moved.json()
    assert any(i["name"] == "rode paprika" for i in body["pantry"])
    assert all(i["name"] != "rode paprika" for i in body["items"])

    # And back to the shopping list.
    back = await client.put(
        "/shopping-list/item", json={"name": "rode paprika", "buy": True}
    )
    body2 = back.json()
    assert any(i["name"] == "rode paprika" for i in body2["items"])
    assert all(i["name"] != "rode paprika" for i in body2["pantry"])


# ---------------------------------------------------------------------------
# Pet food
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_pet_foods_crud(client):
    listed = await client.get("/pet/foods")
    assert listed.status_code == 200
    names = {f["name"] for f in listed.json()}
    assert {"paprika", "wortel"} <= names
    assert all("weightG" in f and "id" in f for f in listed.json())

    created = await client.post("/pet/foods", json={"name": "sla", "weightG": 200})
    assert created.status_code == 200
    body = created.json()
    assert body["name"] == "sla"
    assert body["weightG"] == 200
    assert body["id"]

    deleted = await client.delete(f"/pet/foods/{body['id']}")
    assert deleted.status_code == 200
    after = {f["name"] for f in (await client.get("/pet/foods")).json()}
    assert "sla" not in after


@pytest.mark.asyncio
async def test_pet_get_defaults(client):
    resp = await client.get("/pet")
    assert resp.status_code == 200
    body = resp.json()
    assert body["targetG"] == 1000
    assert body["selection"] == []


@pytest.mark.asyncio
async def test_pet_regenerate_fills_selection(client):
    resp = await client.post("/pet/regenerate")
    assert resp.status_code == 200
    body = resp.json()
    assert body["targetG"] == 1000
    assert len(body["selection"]) >= 1
    for pick in body["selection"]:
        assert {"id", "name", "weightG"} <= set(pick)
    # Persisted and surfaced in the shopping list under Huisdiervoer.
    shopping = (await client.get("/shopping-list")).json()
    pet = [i for i in shopping["items"] if i["group"] == "Huisdiervoer"]
    picked = {p["name"] for p in body["selection"]}
    assert {i["name"] for i in pet} == picked
    assert all(i["quantity"] is None and i["staple"] is False for i in pet)
    # Never in the pantry.
    assert all(i["group"] != "Huisdiervoer" for i in shopping["pantry"])


@pytest.mark.asyncio
async def test_pet_selection_is_priced(client):
    await client.post("/pet/regenerate")
    picked = {
        p["name"] for p in (await client.get("/pet")).json()["selection"]
    }
    quotes = (await client.post("/pricing/quote")).json()["quotes"]
    for q in quotes:
        priced = {i["name"] for i in q["items"]}
        assert picked <= priced


@pytest.mark.asyncio
async def test_pet_target_adjusts_and_reselects(client):
    await client.post("/pet/regenerate")
    resp = await client.put("/pet/target", json={"targetG": 1500})
    assert resp.status_code == 200
    body = resp.json()
    assert body["targetG"] == 1500
    assert len(body["selection"]) >= 1


@pytest.mark.asyncio
async def test_pet_replace_swaps_one(client):
    regen = (await client.post("/pet/regenerate")).json()
    victim = regen["selection"][0]["name"]
    resp = await client.post("/pet/replace", json={"name": victim})
    assert resp.status_code == 200
    body = resp.json()
    # Either it was swapped out, or (list exhausted) it remained — both valid;
    # the selection size never changes on a replace.
    assert len(body["selection"]) == len(regen["selection"])


@pytest.mark.asyncio
async def test_pet_get_reports_zero_coverage_without_overlap(client):
    resp = await client.get("/pet")
    assert resp.status_code == 200
    assert resp.json()["coveredG"] == 0


@pytest.mark.asyncio
async def test_pet_excludes_recipe_overlap_and_reports_coverage(client):
    # Plan the kip-pesto salad (uses ijsbergsla) then regenerate pet food.
    await client.put(
        "/weekmenu/assignments",
        json={
            "date": _today(),
            "recipeId": "salade-kip-pesto",
            "multiplier": 1.0,
        },
    )
    pet = (await client.post("/pet/regenerate")).json()
    assert pet["coveredG"] >= 1  # ijsbergsla contributes coverage
    assert all(f["name"] != "ijsbergsla" for f in pet["selection"])
    sl = (await client.get("/shopping-list")).json()
    huis = [i["name"] for i in sl["items"] if i.get("group") == "Huisdiervoer"]
    assert "ijsbergsla" not in huis  # not duplicated as pet food
    # It is a normal shopping line.
    assert any(i["name"] == "ijsbergsla" for i in sl["items"])


@pytest.mark.asyncio
async def test_deleting_selected_pet_food_scrubs_selection(client):
    # A deleted food must vanish from the selection AND the shopping bag, not
    # linger as a stale name that only the pricing/bag paths still surface.
    regen = (await client.post("/pet/regenerate")).json()
    assert regen["selection"], "expected a non-empty selection to test with"
    victim = regen["selection"][0]
    resp = await client.delete(f"/pet/foods/{victim['id']}")
    assert resp.status_code == 200
    assert all(f["id"] != victim["id"] for f in resp.json())
    # gone from the resolved selection
    pet = (await client.get("/pet")).json()
    assert all(f["name"] != victim["name"] for f in pet["selection"])
    # gone from the shopping bag's Huisdiervoer group
    items = (await client.get("/shopping-list")).json()["items"]
    pet_names = {i["name"] for i in items if i.get("group") == "Huisdiervoer"}
    assert victim["name"] not in pet_names


# ---------------------------------------------------------------------------
# Staples ("heb ik vast wel")
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_staples_crud(client):
    base = await client.get("/staples")
    assert base.status_code == 200
    created = await client.post("/staples", json={"name": "Kaneel"})
    assert created.status_code == 200 and created.json()["name"] == "kaneel"
    sid = created.json()["id"]
    assert any(s["id"] == sid for s in (await client.get("/staples")).json())
    await client.delete(f"/staples/{sid}")
    assert all(s["id"] != sid for s in (await client.get("/staples")).json())


@pytest.mark.asyncio
async def test_added_staple_moves_ingredient_to_pantry(client):
    # Plan a day whose recipe uses 'passata' (normally bought), then mark
    # passata a staple; it must move from the shopping list to the pantry.
    rid = "macaroni-alla-siciliana"
    await client.put(
        "/weekmenu/assignments",
        json={"date": _today(), "recipeId": rid, "multiplier": 1.0},
    )
    await client.post("/staples", json={"name": "passata"})
    sl = (await client.get("/shopping-list")).json()
    assert any(i["name"] == "passata" for i in sl["pantry"])
    assert all(i["name"] != "passata" for i in sl["items"])
