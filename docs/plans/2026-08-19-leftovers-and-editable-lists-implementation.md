# Leftovers + Editable Lists Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Recipe ingredients that are also pet foods are bought once (leftovers cover 50% of the pet's weekly weight); make the "heb ik vast wel" staples and the pet-food lists editable via dedicated pages; fix the bread glaze to plain "melk".

**Architecture:** Extends the ports & adapters backend (FastAPI + Motor + Mongo, uv) and Vue 3 (pnpm) frontend. Staples move from a hardcoded set to a DB collection behind a new `StapleRepo` port; `is_staple` becomes a pure function over an injected set threaded into the shopping partition. `pet_service` stays pure — leftover coverage/exclusion are pure inputs computed by the pet router from the recipe shopping list. Two new management pages (`/staples`, `/pet-foods`).

**Tech Stack:** Python 3.12, FastAPI, Motor, Pydantic v2, uv; Vue 3, Pinia, TypeScript, Vite, pnpm; MongoDB 7; Docker Compose. No new dependencies.

**References:**
- Design: `docs/plans/2026-08-19-leftovers-and-editable-lists-design.md`
- Prior: `docs/plans/2026-08-19-bakes-and-pet-food-*.md`, `2026-08-17-basket-v01-*.md`

**Global rules honored:**
- **Commits:** ONE commit at the very end (Task 14). Every task ends with staging only — never `git commit` mid-plan.
- **No new dependencies.**
- **Python quality:** PEP 8/257/484/561/20; docstrings + type hints; `uv run flake8 app tests` clean; `uv run pytest` after every change.
- **Determinism:** `pet_service` keeps its injectable `random.Random`; no module-level random/clock.

**Current-state reminders (do not break):**
- `app/domain/staples.py` currently exports `STAPLE_INGREDIENTS: frozenset[str]`, `normalize_name(name)`, `is_staple(name)`.
- `is_staple` is used ONLY by `app/services/shopping_service.py::partition_items`. `normalize_name` is used by `menu.py`, `shopping_service.py`.
- `shopping_service.build_breakdown(menu, recipes_by_id)` → `partition_items(items, item_choices)`; shopping router + pricing router call `build_breakdown`.
- Pet endpoints in `app/api/routers/pet.py`; `pet_service.generate/adjust/replace/cheapest`; `PetOut.build(target_g, selection, foods)` in `app/api/schemas/pet.py`.
- Existing repos/ports pattern: see `mongo_pet_food_repo.py` + `ports/pet_food_repo.py`; deps in `app/api/deps.py`; test fixture wiring in `tests/test_api.py`.
- Frontend: `src/router.ts`, `src/App.vue` (nav), `src/api/client.ts`, `src/stores/menu.ts`, `src/components/PetFoodEditor.vue`, `PetPanel.vue`.

---

## Phase A — Editable staples (backend)

### Task 1: `Staple` domain + `StapleRepo` port + Mongo adapter + seed

**Files:**
- Create: `backend/app/domain/staple.py`, `backend/app/ports/staple_repo.py`, `backend/app/adapters/db/mongo_staple_repo.py`
- Modify: `backend/app/seed.py`, `backend/app/api/deps.py`
- Test: `backend/tests/test_staple_repo.py`, extend `backend/tests/test_seed.py`

**Step 1 (failing test):** mongomock round-trip: `MongoStapleRepo.create(Staple(id="", name="Suiker"))` stores it normalized (`"suiker"`); `list`/`delete`/`count` work; `seed_staples_if_empty(repo)` inserts the seed set once (idempotent) and includes `suiker, zwarte sesam, instant gist, basterdsuiker` plus the legacy defaults.
**Step 2:** `cd backend && uv run pytest tests/test_staple_repo.py -v` → FAIL.
**Step 3:**
- `staple.py`: `Staple(BaseModel){id: str, name: str}`.
- `staple_repo.py`: abstract `StapleRepo` (`list`, `create`, `delete`, `count`).
- `mongo_staple_repo.py`: Motor adapter, collection `staples`, `_id`↔`id`, uuid4 id when blank, **store `name` via `normalize_name`** so matching is consistent.
- `seed.py`: `STAPLE_SEED = ["olijfolie","citroensap","chilivlokken","gehakt","rundergehakt","zout","zwarte peper","venkelzaad","suiker","zwarte sesam","instant gist","basterdsuiker"]`; `seed_staples_if_empty(repo)`.
- `deps.py`: `get_staple_repo()`.
**Step 4:** pytest + `uv run flake8 app tests` clean.
**Step 5:** Stage. (No commit.)

---

### Task 2: `is_staple` over an injected set; thread through the partition

**Files:**
- Modify: `backend/app/domain/staples.py`, `backend/app/services/shopping_service.py`
- Test: `backend/tests/test_shopping_service.py`, `backend/tests/test_staples.py`

**Step 1 (failing test):** `is_staple("Suiker", {"suiker"})` is True; `is_staple("macaroni", {"suiker"})` is False. `partition_items(items, item_choices, staples)` puts a staple (name in `staples`) into pantry by default and a non-staple into items; `build_breakdown(menu, recipes_by_id, staples)` threads it.
**Step 2:** FAIL (signature change).
**Step 3:**
- `staples.py`: remove `STAPLE_INGREDIENTS`; change `is_staple(name: str, staples: set[str]) -> bool` → `normalize_name(name) in staples`. Keep `normalize_name`.
- `shopping_service.py`: `partition_items(items, item_choices, staples: set[str])` and `build_breakdown(menu, recipes_by_id, staples: set[str])` — pass `staples` to `is_staple`.
- Update existing tests in `test_shopping_service.py` / `test_staples.py` that call these to pass a staple set (use a fixture set including the legacy names + `suiker`).
**Step 4:** pytest (all) + flake8 clean.
**Step 5:** Stage.

---

### Task 3: Staples API + wire into shopping/pricing routers + startup seed

**Files:**
- Create: `backend/app/api/routers/staples.py`, `backend/app/api/schemas/staple.py`
- Modify: `backend/app/api/routers/shopping.py`, `backend/app/api/routers/pricing.py`, `backend/app/main.py`
- Test: `backend/tests/test_api.py`

**Step 1 (failing test):**
```python
async def test_staples_crud(client):
    base = await client.get("/staples"); assert base.status_code == 200
    created = await client.post("/staples", json={"name": "Kaneel"})
    assert created.status_code == 200 and created.json()["name"] == "kaneel"
    sid = created.json()["id"]
    assert any(s["id"] == sid for s in (await client.get("/staples")).json())
    await client.delete(f"/staples/{sid}")
    assert all(s["id"] != sid for s in (await client.get("/staples")).json())

async def test_added_staple_moves_ingredient_to_pantry(client):
    # add a day recipe that uses 'passata' (normally bought), mark passata a staple
    rid = "macaroni-alla-siciliana"
    await client.put("/weekmenu/assignments", json={"date": _today(), "recipeId": rid, "multiplier": 1.0})
    await client.post("/staples", json={"name": "passata"})
    sl = (await client.get("/shopping-list")).json()
    assert any(i["name"] == "passata" for i in sl["pantry"])
    assert all(i["name"] != "passata" for i in sl["items"])
```
**Step 2:** FAIL.
**Step 3:**
- `schemas/staple.py`: `StapleOut{id,name}`, `StapleIn{name}`.
- `routers/staples.py` (prefix `/staples`): `GET` list, `POST {name}` → create (normalized), `DELETE /{id}`.
- `shopping.py` + `pricing.py`: load staples via `get_staple_repo`, build `staples: set[str]` = `{s.name for s in await repo.list()}`, pass to `build_breakdown`.
- `main.py`: include `staples.router`; startup `seed_staples_if_empty(get_staple_repo())` (guarded with the others).
- `deps.py` already has `get_staple_repo` (Task 1). Test fixture (`tests/test_api.py`): override `get_staple_repo` with a mongomock repo + `seed_staples_if_empty`.
**Step 4:** pytest + flake8 clean.
**Step 5:** Stage.

---

## Phase B — Leftovers (pet/recipe overlap)

### Task 4: `pet_service` coverage + exclude

**Files:**
- Modify: `backend/app/services/pet_service.py`
- Test: `backend/tests/test_pet_service.py`

**Step 1 (failing tests)** (fake prices, `random.Random(0)`):
```python
def test_coverage_g_is_half_standard_weight_of_overlaps():
    foods = [PetFood(id="i", name="ijsbergsla", weight_g=400),
             PetFood(id="p", name="paprika", weight_g=150)]
    assert pet_service.coverage_g(foods, {"ijsbergsla"}) == 200

def test_generate_excludes_overlap_and_fills_effective_target():
    # target 1000, ijsbergsla overlaps -> covered 200 -> effective 800;
    # ijsbergsla never appears in the selection
    foods = [...]  # include ijsbergsla + others
    sel = pet_service.generate(foods, prices, 1000, random.Random(0), exclude_names={"ijsbergsla"})
    assert "ijsbergsla" not in sel

def test_adjust_respects_exclude_and_coverage(): ...
```
**Step 2:** FAIL.
**Step 3:**
- Add `coverage_g(foods, names: set[str]) -> int` = `sum(round(0.5 * f.weight_g) for f in foods if f.name in names)`.
- `generate(foods, prices, target_g, rng, exclude_names: set[str] = frozenset())`: `pool = [f for f in foods if f.name not in exclude_names]`; `effective = max(0, target_g - coverage_g(foods, exclude_names))`; cheapest anchor from `pool`, fill `pool` to `effective`. If `pool` empty → `[]`.
- `adjust(selection, foods, prices, new_target_g, rng, exclude_names=frozenset())`: same effective target + pool; drop any excluded names already in `selection`; then grow/shrink to the effective target keeping the anchor.
- `replace` unchanged, but callers pass the pool (or filter excluded) — keep `replace` signature; the router will pass foods minus excluded so a re-roll never picks an overlap.
**Step 4:** pytest + flake8 clean.
**Step 5:** Stage.

---

### Task 5: Pet router computes overlap from recipes; `PetOut.coveredG`; breakdown dedup

**Files:**
- Modify: `backend/app/api/routers/pet.py`, `backend/app/api/schemas/pet.py`, `backend/app/services/shopping_service.py`
- Test: `backend/tests/test_api.py`, `backend/tests/test_shopping_service.py`

**Step 1 (failing tests):**
```python
async def test_pet_excludes_recipe_overlap_and_reports_coverage(client):
    # plan the kip-pesto salad (uses ijsbergsla) then regenerate pet food
    await client.put("/weekmenu/assignments", json={"date": _today(), "recipeId": "salade-kip-pesto", "multiplier": 1.0})
    pet = (await client.post("/pet/regenerate")).json()
    assert pet["coveredG"] >= 1               # ijsbergsla contributes coverage
    assert all(f["name"] != "ijsbergsla" for f in pet["selection"])
    sl = (await client.get("/shopping-list")).json()
    huis = [i["name"] for i in sl["items"] if i.get("group") == "Huisdiervoer"]
    assert "ijsbergsla" not in huis           # not duplicated as pet food
    assert any(i["name"] == "ijsbergsla" for i in sl["items"])  # it's a normal line
```
Plus a unit test: `build_breakdown` suppresses a pet-selection line whose normalized name equals a recipe item.
**Step 2:** FAIL.
**Step 3:**
- `pet.py`: add `recipe_repo` + build the recipe overlap: load menu, recipes, compute the recipe shopping items via `shopping_service.build_shopping_list(menu, recipes_by_id)` (or reuse the breakdown), collect `recipe_names = {normalize_name(i.name) for i in recipe_items}`; `overlap = {f.name for f in foods if f.name in recipe_names}`. Pass `exclude_names=overlap` to `generate`/`adjust`, and pass `foods` minus overlap to `replace`. Persist selection as before.
- `schemas/pet.py`: `PetOut` gains `coveredG: int`; `PetOut.build(target_g, selection, foods, covered_g=0)`; router passes `pet_service.coverage_g(foods, overlap)`.
- `shopping_service.py`: in the pet-line append (`pet_items` / `build_breakdown`), skip any pet-selection name whose `normalize_name` is already present among the recipe items (dedup).
**Step 4:** pytest + flake8 clean.
**Step 5:** Stage.

---

### Task 6: Seed — new pet foods + bread glaze "melk"

**Files:**
- Modify: `backend/app/seed.py`
- Test: `backend/tests/test_seed.py`

**Step 1 (failing test):** `PET_FOOD_SEED` includes `koolrabi, mais (vers), witlof, babyromaine` with positive `weight_g`; `build_dierbroodjes()` has a `melk` ingredient in the Glans group and NO ingredient whose name contains "ei" in that group.
**Step 2:** FAIL.
**Step 3:**
- Extend `PET_FOOD_SEED`: `koolrabi 300, mais (vers) 250, witlof 150, babyromaine 200`.
- In `build_dierbroodjes`, replace the glaze "melk óf ei" ingredient with a single `Ingredient(group="Glans", name="melk", quantity=None, unit=None, note="dun laagje, optioneel")`.
**Step 4:** pytest + flake8 clean.
**Step 5:** Stage.

---

## Phase C — Frontend

### Task 7: Client types + calls (staples + coveredG)

**Files:**
- Modify: `frontend/src/api/client.ts`

**Step 1:** Add `Staple{id,name}`; `Pet.coveredG: number`. Add calls `listStaples`, `addStaple(name)`, `deleteStaple(id)`; register in the `api` object.
**Step 2:** `cd frontend && pnpm build` type-checks. Stage.

---

### Task 8: Store — staples state/actions; pet coveredG

**Files:**
- Modify: `frontend/src/stores/menu.ts`
- Test: `frontend/tests/menu.store.test.ts`

**Step 1 (failing Vitest):** mock the new client fns; `loadStaples` fills `staples`; `addStaple`/`deleteStaple` update it; `petCovered` reflects `getPet().coveredG`.
**Step 2:** FAIL.
**Step 3:** Add state `staples: Staple[]`, `petCovered: number`; actions `loadStaples`, `addStaple`, `deleteStaple`; set `petCovered` from pet responses in `loadPet/regeneratePet/setPetTarget/replacePetFood`. `loadAll` also `loadStaples`.
**Step 4:** `pnpm vitest run` PASS.
**Step 5:** Stage.

---

### Task 9: `/staples` page

**Files:**
- Create: `frontend/src/views/StaplesView.vue`
- Modify: `frontend/src/router.ts`, `frontend/src/App.vue`

**Step 1:** Route `/staples` → `StaplesView` (list of staple names + add input + remove buttons, using the store). Nav link "Heb ik vast wel" in `App.vue`.
**Step 2:** `pnpm build` type-checks. Stage.

---

### Task 10: `/pet-foods` page

**Files:**
- Create: `frontend/src/views/PetFoodsView.vue`
- Modify: `frontend/src/router.ts`, `frontend/src/App.vue`

**Step 1:** Route `/pet-foods` → `PetFoodsView` wrapping the existing `PetFoodEditor` (self-load pet foods on mount). Nav link "Huisdiervoer". Remove the inline editor from `PetPanel` if it duplicates (keep the panel focused on selection + target + coveredG; link to the page).
**Step 2:** `pnpm build` type-checks. Stage.

---

### Task 11: PetPanel shows coverage

**Files:**
- Modify: `frontend/src/components/PetPanel.vue`

**Step 1:** Show "Huisdiervoer ≈ {{ (petTarget/1000).toFixed(2) }} kg" and, when `petCovered > 0`, a subline "~{{ petCovered }} g uit restjes". Keep ±250 g / Regenereer / replace controls; add a link/button to `/pet-foods`.
**Step 2:** `pnpm build` type-checks. Stage.

---

## Phase D — Integration & finish

### Task 12: End-to-end bring-up

**Step 1:** `cd backend && uv run pytest -v && uv run flake8 app tests` → green.
**Step 2:** `cd frontend && pnpm vitest run && pnpm build` → green.
**Step 3:** `make build && docker compose up -d`; `make ps` healthy.
**Step 4:** Verify:
- `curl -s localhost:18420/staples` → seeded staples incl. `suiker`, `instant gist`, `basterdsuiker`, `zwarte sesam`.
- `curl -s localhost:18420/pet/foods` → includes `koolrabi`, `mais (vers)`, `witlof`, `babyromaine`.
- Plan `salade-kip-pesto` on a day, `POST /pet/regenerate` → `coveredG` > 0 and `ijsbergsla` absent from the pet selection; `GET /shopping-list` shows `ijsbergsla` as a normal line, not under Huisdiervoer.
- `POST /staples {name:"passata"}` then a macaroni day → `passata` appears under pantry, not items.
- Bread recipe glaze shows `melk`, no egg glaze.
- Open the app: `/staples` and `/pet-foods` pages load, add/remove works.
- Clear test state in Mongo afterward (`db.weekmenu.deleteMany({})`).
**Step 5:** Update `README.md` (leftovers, editable lists + pages). Stage.

---

### Task 13: Final review pass

**Step 1:** Re-run both quality gates; confirm green. Spot-check: `is_staple` set-threading has no stragglers (grep for old `STAPLE_INGREDIENTS`/`is_staple(` one-arg calls); pet overlap uses normalized names consistently; no module-level randomness.
**Step 2:** Stage any fixes.

---

### Task 14: Single final commit

**Step 1:** `git add -A && git status` (review — includes design + plan docs; no caches).
**Step 2:** One commit (user rule; no AI mentions):
```bash
git commit -m "feat: leftovers cover pet food and make staple/pet lists editable"
```
**Step 3:** `git push` (may need the user's ssh-agent; if it fails, report and leave the commit).

---

## Task dependency notes
- Task 1 → 2 → 3 (staple data → is_staple threading → API/routers).
- Task 4 → 5 (pet_service coverage before the router uses it); Task 5 depends on Task 2's `build_breakdown(..., staples)` signature — pass staples through in the pet router's shopping call too.
- Frontend 7 → 8 → 9/10/11. Task 12 needs everything; Task 14 last (single-commit rule).

## Verification checklist (before claiming done)
- [ ] `uv run pytest` green; `uv run flake8 app tests` clean.
- [ ] `pnpm vitest run` green; `pnpm build` clean.
- [ ] Containers healthy; leftovers reduce the pet target and de-duplicate overlaps; `/staples` and `/pet-foods` pages work; added staple moves an ingredient to pantry; bread glaze is "melk".
- [ ] Exactly one commit on `feat/basket-v01`, no AI mentions (pushed if ssh-agent allows).
