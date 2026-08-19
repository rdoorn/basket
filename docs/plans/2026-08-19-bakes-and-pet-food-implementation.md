# Bake Recipes + Pet Food Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add non-day "bake" recipes with a calendar "Extra's" drop zone, and a generic weight-driven pet-food generator (cheapest + random fill, re-rollable), both feeding the shopping bag and Buy page.

**Architecture:** Extends the existing ports & adapters backend (FastAPI + Motor + Mongo) and Vue 3 (pnpm) frontend. New `pet_service` uses the existing `pricing_provider` port for "cheapest" and an injectable RNG; a new `pet_food_repo` port + Mongo adapter holds the editable food list. `WeekMenu` carries the new bag state (`extras`, `pet_target_g`, `pet_selection`).

**Tech Stack:** Python 3.12, FastAPI, Motor, Pydantic v2, uv; Vue 3, Pinia, TypeScript, Vite, pnpm; MongoDB 7; Docker Compose. No new dependencies.

**References:**
- Design: `docs/plans/2026-08-19-bakes-and-pet-food-design.md`
- Prior design/plan: `docs/plans/2026-08-17-basket-v01-*.md`

**Global rules honored:**
- **Commits:** ONE commit at the very end (Task 16). Every task ends with `git add` staging only — never `git commit` mid-plan. (User rule: only commit once, when all tasks are complete.)
- **Dependency freshness:** no new libraries are added, so nothing to pin. Do not introduce any.
- **Python quality:** PEP 8/257/484/561/20; docstrings + type hints; `uv run flake8 app tests` clean; `uv run pytest` after every change.
- **Determinism:** no `Math.random`/`random` at import; `pet_service` takes an injectable `random.Random` so tests seed it.

**Current contract reminders (do not break):**
- `GET /weekmenu` → `{ days: [{date, assignment|null}] }`; assignments camelCase `{recipeId, multiplier}`.
- `GET /shopping-list` → `{ items, pantry }`; items/pantry are `ShoppingListItem` `{name, quantity, unit, source, staple}`.
- `WeekMenu` already has `assignments: dict[str, DayAssignment]` and `item_choices: dict[str, bool]`.
- Recipe DTOs are snake_case; menu/bag DTOs are camelCase.

---

## Phase A — Bake recipes + Extra's zone (backend)

### Task 1: Recipe `category` field

**Files:**
- Modify: `backend/app/domain/recipe.py`
- Test: `backend/tests/test_domain.py`

**Step 1 (failing test):**
```python
from app.domain.recipe import Recipe


def test_recipe_defaults_to_meal_category():
    r = Recipe(id="x", title="t", icon="🍝", description="", servings=2)
    assert r.category == "meal"


def test_recipe_accepts_bake_category():
    r = Recipe(id="x", title="t", icon="🍞", description="", servings=8, category="bake")
    assert r.category == "bake"
```
**Step 2:** `cd backend && uv run pytest tests/test_domain.py -k category -v` → FAIL.
**Step 3:** Add `category: Literal["meal", "bake"] = "meal"` to `Recipe` (import `Literal` already present). Keep it optional/defaulted so existing recipes and the `RecipeInput` create/update path need no change.
**Step 4:** pytest → PASS; `uv run flake8 app tests` clean.
**Step 5:** Stage `recipe.py` + test. (No commit.)

> Note: recipe create/update DTOs mirror the domain `Recipe`, so `category` is accepted automatically. Verify the recipe list card DTO includes `category` if the frontend needs to badge bakes — add it to the card schema in this task if absent.

---

### Task 2: `ExtraAssignment` + `WeekMenu.extras`

**Files:**
- Modify: `backend/app/domain/menu.py`
- Test: `backend/tests/test_domain.py`

**Step 1 (failing test):**
```python
from app.domain.menu import WeekMenu, ExtraAssignment


def test_extras_add_update_remove():
    m = WeekMenu()
    m.set_extra("bread", 1.0)
    assert m.extras == [ExtraAssignment(recipe_id="bread", multiplier=1.0)]
    m.set_extra("bread", 2.0)  # update in place, no duplicate
    assert len(m.extras) == 1 and m.extras[0].multiplier == 2.0
    m.remove_extra("bread")
    assert m.extras == []
```
**Step 2:** run → FAIL.
**Step 3:** Add `ExtraAssignment(BaseModel){recipe_id: str, multiplier: float = 1.0}`; add `extras: list[ExtraAssignment] = Field(default_factory=list)` to `WeekMenu`; add `set_extra(recipe_id, multiplier)` (upsert by recipe_id) and `remove_extra(recipe_id)`.
**Step 4:** pytest + flake8 clean.
**Step 5:** Stage.

---

### Task 3: Fold extras into the shopping list

**Files:**
- Modify: `backend/app/services/shopping_service.py`
- Test: `backend/tests/test_shopping_service.py`

**Step 1 (failing test):** with a recipe `B` (macaroni 350 g), assign it to a day at 1× AND add it as an extra at 2×; assert `build_shopping_list` totals macaroni = 350 + 700 = 1050 g. (Extras aggregate exactly like day assignments.)
**Step 2:** FAIL.
**Step 3:** In `build_shopping_list`, after iterating `menu.assignments.values()`, also iterate `menu.extras` (each `ExtraAssignment` → look up recipe, scale ingredients by `multiplier`, aggregate with the same keying/merge policy). Extract the per-assignment inner loop into a small local helper to stay DRY.
**Step 4:** pytest (all) + flake8 clean.
**Step 5:** Stage.

---

### Task 4: Extras API (weekmenu router + schemas)

**Files:**
- Modify: `backend/app/api/schemas/menu.py`, `backend/app/api/routers/weekmenu.py`
- Test: `backend/tests/test_api.py`

**Step 1 (failing test):**
```python
async def test_extras_add_and_remove(client):
    rid = "macaroni-alla-siciliana"
    r = await client.put("/weekmenu/extras", json={"recipeId": rid, "multiplier": 2.0})
    assert r.status_code == 200
    assert any(e["recipeId"] == rid and e["multiplier"] == 2.0 for e in r.json()["extras"])
    got = await client.get("/weekmenu")
    assert any(e["recipeId"] == rid for e in got.json()["extras"])
    d = await client.delete(f"/weekmenu/extras/{rid}")
    assert all(e["recipeId"] != rid for e in d.json()["extras"])
```
**Step 2:** FAIL.
**Step 3:**
- Add `ExtraOut {recipeId, multiplier}` and include `extras: list[ExtraOut]` in `WindowOut` (the `GET /weekmenu` response) and in `WeekMenuOut`.
- `PUT /weekmenu/extras` body `{recipeId, multiplier}` → load menu, `set_extra`, save, return `WeekMenuOut` (must include `extras`).
- `DELETE /weekmenu/extras/{recipe_id}` → load, `remove_extra`, save, return.
- Ensure the mongo menu repo persists `extras` (Task 5 covers it — order Task 5 before running the API test, or stub then).
**Step 4:** pytest + flake8 clean.
**Step 5:** Stage.

---

### Task 5: Persist `extras` (+ pet fields) in the Mongo menu repo

**Files:**
- Modify: `backend/app/adapters/db/mongo_menu_repo.py`
- Test: `backend/tests/test_mongo_repos.py`

**Step 1 (failing test):** save a `WeekMenu` with an extra and (foreshadowing) `pet_target_g=1250`, `pet_selection=["paprika"]`; load; assert all round-trip. (Add pet asserts once Task 8 adds those fields; for now assert `extras`.)
**Step 2:** FAIL.
**Step 3:** In `load`, read `extras`, `pet_target_g` (default 1000), `pet_selection` (default []) from the doc; in `save`, include them from `model_dump()`. Keep `assignments` + `item_choices` as-is.
**Step 4:** pytest + flake8 clean.
**Step 5:** Stage.

---

### Task 6: Seed the bread recipe (`category: "bake"`)

**Files:**
- Modify: `backend/app/seed.py`
- Test: `backend/tests/test_seed.py`

**Step 1 (failing test):** `build_dierbroodjes()` returns `category=="bake"`, `icon=="🍞"`, `servings==8`, `>=10` steps, a `prep`? (no — it has mixing/kneading; phases are `cook`/`finish` as appropriate; at least assert steps span multiple phases), ingredient `broodmeel` 310 g present; and `seed_recipes()` now returns 5 with unique ids.
**Step 2:** FAIL.
**Step 3:** Add `build_dierbroodjes()` transcribing the recipe faithfully:
- id `zachte-dierbroodjes`, title "Zachte Dierbroodjes (Japanse/Koreaanse stijl)", icon 🍞, category "bake", servings 8, total_time approx (kneading ~20 + koelen 30 + rijs 60–90 + bakken 20–23 → set total_time_min_low=150 high=185; note these include rijstijd).
- Ingredient groups **Deeg** (broodmeel 310 g, suiker 28 g, zout 3 g, instant gist 3.5 g, ei 56 g, melk 155 g, ongezouten boter 31 g), **Decoratie** (zwarte sesam, ham, nori — qty None with notes), **Glans** (melk óf losgeklopt ei — None, optioneel).
- Steps 1–10 verbatim-elaborate (mengen, eerste kneedfase, boter toevoegen, uitkneden, koelen 30 min vriezer, verdelen ~73 g, dieren vormen, tweede rijs 60–90 vingertest, decoreren, bakken 170 °C 20–23 min / kern 93–95 °C, 5 min laten liggen, 20–30 min afkoelen). Preserve reasoning/tips. Phases: mixing/kneading/koelen/bakken → `cook`; vormen/decoreren/afkoelen → `prep`/`finish` sensibly.
- Add `build_dierbroodjes()` to `seed_recipes()` list.
**Step 4:** pytest + flake8 clean.
**Step 5:** Stage.

---

## Phase B — Pet food (backend)

### Task 7: `PetFood` domain + `pet_foods` port & Mongo adapter + seed

**Files:**
- Create: `backend/app/domain/pet.py`, `backend/app/ports/pet_food_repo.py`, `backend/app/adapters/db/mongo_pet_food_repo.py`
- Modify: `backend/app/seed.py`, `backend/app/api/deps.py`
- Test: `backend/tests/test_pet_repo.py`, extend `backend/tests/test_seed.py`

**Step 1 (failing test):** with mongomock, `MongoPetFoodRepo.create/list/delete` round-trip a `PetFood(name, weight_g)`; `seed_pet_foods_if_empty(repo)` inserts the seed list once (idempotent).
**Step 2:** FAIL.
**Step 3:**
- `pet.py`: `PetFood(BaseModel){id: str, name: str, weight_g: int}` and `PetSelectionItem(BaseModel){name: str}` (or reuse plain names).
- `pet_food_repo.py`: abstract `PetFoodRepo` with async `list`, `create`, `delete`, `count`.
- `mongo_pet_food_repo.py`: Motor adapter (collection `pet_foods`, `_id`↔`id`, uuid4 id when absent).
- `seed.py`: `PET_FOOD_SEED = [PetFood(...paprika 150, komkommer 400, ijsbergsla 400, wortel 80, andijvie 300, veldsla 100...)]` and `seed_pet_foods_if_empty(repo)`.
- `deps.py`: `get_pet_food_repo()` bound to the shared db.
**Step 4:** pytest + flake8 clean.
**Step 5:** Stage.

---

### Task 8: `WeekMenu` pet fields + `pet_service` selection

**Files:**
- Modify: `backend/app/domain/menu.py`
- Create: `backend/app/services/pet_service.py`
- Test: `backend/tests/test_pet_service.py`

**Step 1 (failing tests)** (use a fake pricing provider with fixed prices and `random.Random(0)`):
```python
# fill_to_weight: cheapest anchor first, then randoms until summed weight_g >= target
def test_generate_starts_with_cheapest_then_fills_to_target(): ...
# short list can't loop forever (cap at list length)
def test_generate_caps_at_list_size(): ...
# replace swaps one pick for a random unselected food; no-op when none left
def test_replace_swaps_for_unselected(): ...
def test_replace_noop_when_all_selected(): ...
# adjust target grows (adds) / shrinks (drops trailing, keeps anchor)
def test_adjust_target_grows_and_shrinks(): ...
```
**Step 2:** FAIL.
**Step 3:**
- `menu.py`: add `pet_target_g: int = 1000` and `pet_selection: list[str] = Field(default_factory=list)`.
- `pet_service.py`, all pure (inputs: `foods: list[PetFood]`, `prices: dict[str, float]` or a `PricingProvider`, `rng: random.Random`):
  - `cheapest(foods, prices) -> PetFood`.
  - `generate(foods, prices, target_g, rng) -> list[str]`: anchor = cheapest; then repeatedly pick a random not-yet-selected food, accumulating `weight_g`, until `>= target_g` or all foods used.
  - `replace(selection, foods, name, rng) -> list[str]`: swap `name` for a random food not in `selection`; return unchanged if none available.
  - `adjust(selection, foods, prices, new_target_g, rng) -> list[str]`: if summed weight < target, add randoms; if over by a whole item, drop trailing non-anchor picks; keep the cheapest anchor.
  - Keep "cheapest" behind the pricing port: the service takes a `prices` map so tests inject; the router builds the map by quoting foods once via the provider.
**Step 4:** pytest + flake8 clean.
**Step 5:** Stage.

---

### Task 9: Pet API (router + schemas + deps wiring)

**Files:**
- Create: `backend/app/api/routers/pet.py`, `backend/app/api/schemas/pet.py`
- Modify: `backend/app/main.py` (include router + seed pet foods on startup)
- Test: `backend/tests/test_api.py`

**Step 1 (failing tests):**
```python
async def test_pet_foods_crud(client): ...           # GET/POST/DELETE /pet/foods
async def test_pet_get_and_regenerate(client):       # POST /pet/regenerate fills selection
async def test_pet_target_adjust(client):            # PUT /pet/target changes target + reselects
async def test_pet_replace(client):                  # POST /pet/replace swaps one
```
(The API fixture must also override `get_pet_food_repo`; add pet-food seeding in the fixture.)
**Step 2:** FAIL.
**Step 3:**
- `schemas/pet.py`: `PetFoodOut{id,name,weightG}`, `PetFoodIn{name,weightG}`, `PetOut{targetG, selection: list[PetFoodOut]}`, `PetTargetIn{targetG}` (or `{deltaG}`), `PetReplaceIn{name}`.
- `pet.py` router (prefix `/pet`): `GET/POST /foods`, `DELETE /foods/{id}`, `GET ""`, `PUT /target`, `POST /regenerate`, `POST /replace`. Each mutation loads menu, reads pet foods, builds the price map via the pricing providers (use the cheapest across providers, or the first provider — document choice), calls `pet_service`, persists `pet_selection`/`pet_target_g` on the menu, returns `PetOut`.
- `main.py`: include `pet.router`; in lifespan, also `seed_pet_foods_if_empty(get_pet_food_repo())` (guarded).
**Step 4:** pytest + flake8 clean.
**Step 5:** Stage.

---

### Task 10: Pet foods + extras in shopping list & pricing

**Files:**
- Modify: `backend/app/services/shopping_service.py`, `backend/app/api/routers/shopping.py`, `backend/app/api/routers/pricing.py`, `backend/app/domain/shopping.py`
- Test: `backend/tests/test_api.py`, `backend/tests/test_shopping_service.py`

**Step 1 (failing test):** after `POST /pet/regenerate` with a known food list, `GET /shopping-list` includes those foods grouped as pet items; `POST /pricing/quote` prices them. Extras (Task 3) already fold into items.
**Step 2:** FAIL.
**Step 3:**
- `ShoppingListItem` gains `group: str | None = None` (e.g. `"Huisdiervoer"`) so the UI can section pet foods. Recipe-derived items keep `group=None`.
- `build_breakdown` (or the shopping router) appends the pet selection as `ShoppingListItem(name, quantity=None, unit=None, source="supermarket", staple=False, group="Huisdiervoer")` — one line per selected food (no per-item grams, per design). Pet items are **not** staples and always land in `items` (buyable), never pantry.
- Pricing already prices `breakdown.items`; confirm pet items are included in the quote.
**Step 4:** pytest + flake8 clean.
**Step 5:** Stage.

---

## Phase C — Frontend

### Task 11: API client types + calls

**Files:**
- Modify: `frontend/src/api/client.ts`
- Test: (covered via store tests in Task 13)

**Step 1:** Add types: `Recipe.category`, `RecipeCard.category`, `Extra{recipeId,multiplier}`, `WeekMenu.extras`, `PetFood{id,name,weightG}`, `Pet{targetG,selection:PetFood[]}`, `ShoppingItem.group`. Add calls: `putExtra`, `deleteExtra`, `listPetFoods`, `addPetFood`, `deletePetFood`, `getPet`, `setPetTarget`, `regeneratePet`, `replacePetFood`. Add each to the `api` object.
**Step 2:** `cd frontend && pnpm build` type-checks. Stage.

---

### Task 12: Store state + actions

**Files:**
- Modify: `frontend/src/stores/menu.ts`
- Test: `frontend/tests/menu.store.test.ts`

**Step 1 (failing Vitest):** mock the new client fns; test `addExtra`/`removeExtra` update `extras`; `regeneratePet`/`setPetTarget`/`replacePetFood` update `petTarget`+`petSelection`; `loadAll` also loads extras + pet.
**Step 2:** FAIL.
**Step 3:** Add state `extras`, `petTarget`, `petSelection`, `petFoods`; actions calling the client then refreshing shopping list. `loadAll` fetches pet + foods too.
**Step 4:** `pnpm vitest run` PASS.
**Step 5:** Stage.

---

### Task 13: Extra's drop zone UI

**Files:**
- Modify: `frontend/src/views/CalendarView.vue`
- Create: `frontend/src/components/ExtrasZone.vue`
- Reuse: `frontend/src/lib/dnd.ts` (`RECIPE_MIME`)

**Step 1:** `ExtrasZone` accepts recipe-card drops (dragover sets `dropEffect='copy'` via `dropEffectForTypes`), lists extra cards with a `PortionSelector` and a remove button, and (clicking a card) opens the recipe detail. Wire drop → `store.addExtra(recipeId, 1)`; multiplier → update; remove → `store.removeExtra`. Badge bakes 🍞 in the library (`RecipeCard`/library section using `recipe.category`).
**Step 2:** `pnpm build` type-checks. Manual DnD check happens in Task 15.
**Step 3:** Stage.

---

### Task 14: "Huisdiervoer" panel + pet-food editor

**Files:**
- Create: `frontend/src/components/PetPanel.vue`, `frontend/src/components/PetFoodEditor.vue`
- Modify: `frontend/src/views/CalendarView.vue`, `frontend/src/components/ShoppingList.vue` (group header for "Huisdiervoer" if pet items surface there)

**Step 1:**
- `PetPanel`: shows "Huisdiervoer ≈ {{ (targetG/1000).toFixed(2) }} kg" with **−250 g / +250 g** buttons (call `setPetTarget`), a **Regenereer** button, and the selected foods list each with a **↻ replace** button (`replacePetFood(name)`).
- `PetFoodEditor`: an add row (name + grams) + list with remove, calling `addPetFood`/`deletePetFood`. A collapsible section or small modal opened from the panel.
- Place `PetPanel` in the calendar's right column beside the shopping list / pantry.
**Step 2:** `pnpm build` type-checks. Stage.

---

## Phase D — Integration & finish

### Task 15: End-to-end bring-up

**Step 1:** `cd backend && uv run pytest -v && uv run flake8 app tests` → green.
**Step 2:** `cd frontend && pnpm vitest run && pnpm build` → green.
**Step 3:** `make build && docker compose up -d` (or rebuild `api`+`frontend`); wait; `make ps` healthy.
**Step 4:** Verify:
- `curl -s localhost:18420/recipes` → 5 recipes incl. `zachte-dierbroodjes` (category bake).
- Drag the bread into **Extra's** (browser) → its ingredients appear in the shopping list.
- `curl -s -X POST localhost:18420/pet/regenerate` → selection non-empty; `GET /shopping-list` shows a "Huisdiervoer" group; `POST /pricing/quote` prices them.
- `PUT /pet/target {targetG:1500}` grows the selection; `POST /pet/replace {name:...}` swaps one.
- Clear test state in Mongo afterward for a clean slate (drop `weekmenu`).
**Step 5:** Update `README.md` (bakes + Extra's + Huisdiervoer). Stage.

---

### Task 16: Single final commit

**Step 1:** Re-run both quality gates (backend pytest+flake8, frontend vitest+build); confirm green.
**Step 2:** Confirm on branch `feat/basket-v01` (already the working branch).
**Step 3:** `git add -A && git status` (review — includes both design docs + this plan; no caches).
**Step 4:** One commit (per user rule; no AI mentions):
```bash
git commit -m "feat: add bake recipes with an Extra's zone and a pet-food generator"
```
**Step 5:** `git push`.

---

## Task dependency notes
- Do Tasks 1–2 before 3–4; do Task 5 (repo persistence) before running Task 4/9 API tests that reload the menu.
- Task 7 before 8–9 (pet repo/domain before service/API).
- Task 10 depends on 3 (extras folding) and 9 (pet selection persisted).
- Frontend 11 → 12 → 13/14. Task 15 needs everything; Task 16 last (single-commit rule).

## Verification checklist (before claiming done)
- [ ] `uv run pytest` green; `uv run flake8 app tests` clean.
- [ ] `pnpm vitest run` green; `pnpm build` clean.
- [ ] Containers healthy; bread draggable into Extra's; pet generator fills/《regenerates》/replaces; both appear in shopping list + Buy page.
- [ ] Pet weekly total shown in kg with ±250 g; no per-item grams.
- [ ] Exactly one commit on `feat/basket-v01`, pushed, no AI mentions.
