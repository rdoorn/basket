# Basket v0.1 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a containerized, no-login web app to plan a 14-day menu by dragging recipes onto a calendar, derive a scaled shopping list, and view per-store prices via a mock pricing adapter.

**Architecture:** Ports & adapters (hexagonal). Vue 3 (pnpm) → REST/JSON → FastAPI (uv) → services → ports → adapters (MongoDB, pricing). Stores and DB are adapters; the domain imports no framework. Pricing has a mock adapter now; real AH/Picnic slot into the same port later.

**Tech Stack:** Python 3.12 + FastAPI + Motor (async Mongo) + Pydantic v2, managed by `uv`. Vue 3 + Vite + Pinia + TypeScript, managed by `pnpm`. MongoDB 7. Docker Compose + Makefile.

**Global rules honored:**
- **Commits:** one commit at the very end (Task 16). Every task ends with `git add` staging only — **never** `git commit` mid-plan.
- **Dependency freshness (3 days):** uv `exclude-newer = "2026-08-14"`; pnpm `minimumReleaseAge: 4320` (minutes). Pin all versions.
- **Python quality:** PEP 8/257/484/561/20; flake8 must pass; pytest after every change.
- **Ports (non-obvious, host-reachable):** Mongo `47017`, API `18420`, Frontend `8173`.

**Reference:** design at `docs/plans/2026-08-17-basket-v01-design.md`.

---

## Phase 0 — Scaffolding & containers

### Task 1: Repo skeleton + tooling config

**Files:**
- Create: `backend/pyproject.toml`
- Create: `backend/app/__init__.py`, `backend/tests/__init__.py`
- Create: `backend/.flake8`
- Create: `frontend/.gitignore`, `backend/.gitignore`

**Step 1:** Create `backend/pyproject.toml`:

```toml
[project]
name = "basket-backend"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "fastapi==0.115.6",
    "uvicorn[standard]==0.34.0",
    "motor==3.6.0",
    "pydantic==2.10.4",
    "pydantic-settings==2.7.0",
]

[dependency-groups]
dev = [
    "pytest==8.3.4",
    "pytest-asyncio==0.25.0",
    "mongomock-motor==0.0.34",
    "flake8==7.1.1",
    "httpx==0.28.1",
]

[tool.uv]
exclude-newer = "2026-08-14T00:00:00Z"

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

> Before running, verify each pinned version has a release older than 2026-08-14 with
> `uv pip index versions <pkg>` (or check PyPI). If a pin is too new, step back to the
> newest release published on/before 2026-08-14. `exclude-newer` enforces this anyway.

**Step 2:** Create `backend/.flake8`:

```ini
[flake8]
max-line-length = 100
extend-ignore = E203, W503
exclude = .venv,__pycache__
```

**Step 3:** Create `backend/.gitignore` and `frontend/.gitignore` (`.venv`, `__pycache__`, `node_modules`, `dist`, `.pytest_cache`).

**Step 4:** Bootstrap the venv and lock:

Run: `cd backend && uv sync`
Expected: `.venv` created, dependencies resolved, `uv.lock` written.

**Step 5:** Stage: `git add backend/pyproject.toml backend/.flake8 backend/.gitignore frontend/.gitignore backend/uv.lock backend/app/__init__.py backend/tests/__init__.py`

---

### Task 2: Backend config module

**Files:**
- Create: `backend/app/config.py`
- Test: `backend/tests/test_config.py`

**Step 1 (test first):**

```python
from app.config import Settings


def test_defaults_use_non_obvious_ports():
    s = Settings(_env_file=None)
    assert "47017" in s.mongo_url
    assert s.api_port == 18420
    assert s.mongo_db == "basket"


def test_env_override(monkeypatch):
    monkeypatch.setenv("API_PORT", "9999")
    s = Settings(_env_file=None)
    assert s.api_port == 9999
```

**Step 2:** Run `cd backend && uv run pytest tests/test_config.py -v` → FAIL (no module).

**Step 3:** Implement `backend/app/config.py`:

```python
"""Application configuration loaded from the environment."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings for the Basket API."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    mongo_url: str = "mongodb://mongo:47017"
    mongo_db: str = "basket"
    api_port: int = 18420


def get_settings() -> Settings:
    """Return a cached settings instance."""
    return Settings()
```

**Step 4:** Run pytest → PASS. Run `uv run flake8 app tests` → clean.

**Step 5:** Stage the two files.

---

### Task 3: Docker Compose + Makefile + Dockerfiles

**Files:**
- Create: `backend/Dockerfile`
- Create: `frontend/Dockerfile`
- Create: `docker-compose.yml`
- Create: `Makefile`
- Create: `.env.example`

**Step 1:** `backend/Dockerfile` (uv-based):

```dockerfile
FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /bin/uv
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev
COPY app ./app
EXPOSE 18420
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "18420"]
```

**Step 2:** `frontend/Dockerfile` (pnpm dev server for v0.1):

```dockerfile
FROM node:22-slim
RUN corepack enable
WORKDIR /app
COPY package.json pnpm-lock.yaml .npmrc ./
RUN pnpm install --frozen-lockfile
COPY . .
EXPOSE 8173
CMD ["pnpm", "dev", "--host", "0.0.0.0", "--port", "8173"]
```

**Step 3:** `docker-compose.yml`:

```yaml
services:
  mongo:
    image: mongo:7.0
    command: ["--port", "47017"]
    ports:
      - "47017:47017"
    volumes:
      - mongo_data:/data/db

  api:
    build: ./backend
    environment:
      MONGO_URL: "mongodb://mongo:47017"
      MONGO_DB: "basket"
      API_PORT: "18420"
    ports:
      - "18420:18420"
    depends_on:
      - mongo

  frontend:
    build: ./frontend
    environment:
      VITE_API_BASE: "http://localhost:18420"
    ports:
      - "8173:8173"
    depends_on:
      - api

volumes:
  mongo_data:
```

**Step 4:** `Makefile`:

```makefile
.PHONY: build up down logs restart ps test-backend

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

restart: down up

ps:
	docker compose ps

test-backend:
	cd backend && uv run pytest -v && uv run flake8 app tests
```

**Step 5:** `.env.example` documenting `MONGO_URL`, `MONGO_DB`, `API_PORT`, `VITE_API_BASE`.

**Step 6:** Stage all created files. (Do not build yet — frontend package files come in Phase 3.)

---

## Phase 1 — Domain & services (pure, no I/O)

### Task 4: Domain entities

**Files:**
- Create: `backend/app/domain/__init__.py`, `recipe.py`, `menu.py`, `shopping.py`, `pricing.py`
- Test: `backend/tests/test_domain.py`

**Step 1 (test first):**

```python
from app.domain.recipe import Recipe, Ingredient, Step
from app.domain.menu import WeekMenu, DayAssignment


def test_ingredient_scaled():
    ing = Ingredient(name="macaroni", quantity=350, unit="g")
    assert ing.scaled(2.0).quantity == 700
    assert ing.scaled(0.5).quantity == 175


def test_ingredient_scaled_none_quantity_stays_none():
    ing = Ingredient(name="laurierblad", quantity=None, unit=None)
    assert ing.scaled(2.0).quantity is None


def test_weekmenu_assign_and_get():
    m = WeekMenu()
    m.set("2026-08-17", DayAssignment(recipe_id="r1", multiplier=1.0))
    assert m.get("2026-08-17").recipe_id == "r1"
```

**Step 2:** Run `uv run pytest tests/test_domain.py -v` → FAIL.

**Step 3:** Implement entities as Pydantic v2 models. Key rules:
- `Ingredient`: fields `group: str | None`, `name: str`, `quantity: float | None`, `unit: str | None`, `note: str | None`, and reserved `normalized_name: str | None = None`, `brand_override: str | None = None`, `source: str = "supermarket"`. Method `scaled(factor: float) -> Ingredient` multiplies `quantity` when not `None`.
- `Step`: `order: int`, `title: str`, `phase: Literal["prep","cook","finish"]`, `duration_min_low: int | None`, `duration_min_high: int | None`, `instructions: str`.
- `Recipe`: `id`, `title`, `icon: str`, `description`, `servings: int`, `total_time_min_low/high`, `tags: list[str]`, `notes: str | None`, `ingredients: list[Ingredient]`, `steps: list[Step]`.
- `menu.py`: `DayAssignment(recipe_id: str, multiplier: float = 1.0)`; `WeekMenu` wrapping `assignments: dict[str, DayAssignment]` with `set/get/remove/move_or_swap`.
- `shopping.py`: `ShoppingListItem(name, quantity, unit, source)`.
- `pricing.py`: `PricedItem(name, quantity, unit, unit_price, line_total)`, `StoreQuote(store, items, total)`.

**Step 4:** Run pytest → PASS; flake8 → clean.

**Step 5:** Stage the domain files + test.

---

### Task 5: Menu service — move/swap resolution

**Files:**
- Create: `backend/app/services/__init__.py`, `menu_service.py`
- Test: `backend/tests/test_menu_service.py`

**Step 1 (test first):**

```python
from app.domain.menu import WeekMenu, DayAssignment
from app.services.menu_service import move_or_swap


def _menu():
    m = WeekMenu()
    m.set("d1", DayAssignment(recipe_id="A", multiplier=1.0))
    return m


def test_move_to_empty_day():
    m = _menu()
    move_or_swap(m, src="d1", dst="d2")
    assert m.get("d2").recipe_id == "A"
    assert m.get("d1") is None


def test_swap_two_days():
    m = _menu()
    m.set("d2", DayAssignment(recipe_id="B", multiplier=2.0))
    move_or_swap(m, src="d1", dst="d2")
    assert m.get("d2").recipe_id == "A"
    assert m.get("d1").recipe_id == "B"
    assert m.get("d1").multiplier == 2.0
```

**Step 2:** Run → FAIL. **Step 3:** Implement `move_or_swap(menu, src, dst)`: pop src; if dst occupied, put dst's assignment at src, else clear src; put src's assignment at dst. Also add `assign(menu, date, recipe_id, multiplier)` for the recipe→day drop. **Step 4:** pytest PASS, flake8 clean. **Step 5:** Stage.

---

### Task 6: Shopping service — aggregate + scale

**Files:**
- Create: `backend/app/services/shopping_service.py`
- Test: `backend/tests/test_shopping_service.py`

**Step 1 (test first):**

```python
from app.domain.recipe import Recipe, Ingredient
from app.domain.menu import WeekMenu, DayAssignment
from app.services.shopping_service import build_shopping_list


def _recipe():
    return Recipe(
        id="A", title="t", icon="🍝", description="", servings=4,
        total_time_min_low=50, total_time_min_high=60, tags=[], notes=None,
        ingredients=[
            Ingredient(name="macaroni", quantity=350, unit="g"),
            Ingredient(name="ui", quantity=1, unit="stuk"),
        ],
        steps=[],
    )


def test_scales_and_aggregates_same_ingredient():
    menu = WeekMenu()
    menu.set("d1", DayAssignment(recipe_id="A", multiplier=1.0))
    menu.set("d2", DayAssignment(recipe_id="A", multiplier=2.0))
    items = build_shopping_list(menu, {"A": _recipe()})
    by_name = {i.name: i for i in items}
    assert by_name["macaroni"].quantity == 1050  # 350 + 700
    assert by_name["ui"].quantity == 3
```

**Step 2:** FAIL. **Step 3:** Implement `build_shopping_list(menu, recipes_by_id)`: for each assignment, look up recipe, scale each ingredient by multiplier, aggregate by `(normalized_name or name, unit)`, summing quantities (skip aggregation math when quantity is `None` — keep it listed once). Return `list[ShoppingListItem]` sorted by name. **Step 4:** PASS, flake8 clean. **Step 5:** Stage.

---

### Task 7: Pricing port + mock adapter + pricing service

**Files:**
- Create: `backend/app/ports/__init__.py`, `pricing_provider.py`
- Create: `backend/app/adapters/__init__.py`, `adapters/pricing/__init__.py`, `mock_provider.py`
- Create: `backend/app/services/pricing_service.py`
- Test: `backend/tests/test_pricing_service.py`

**Step 1 (test first):**

```python
from app.domain.shopping import ShoppingListItem
from app.adapters.pricing.mock_provider import MockPricingProvider
from app.services.pricing_service import quote_all


def test_quote_all_returns_totals_per_store():
    items = [ShoppingListItem(name="macaroni", quantity=350, unit="g", source="supermarket")]
    quotes = quote_all(items, [MockPricingProvider("Albert Heijn"), MockPricingProvider("Picnic")])
    assert {q.store for q in quotes} == {"Albert Heijn", "Picnic"}
    for q in quotes:
        assert q.total == sum(i.line_total for i in q.items)
```

**Step 2:** FAIL. **Step 3:** Implement:
- `ports/pricing_provider.py`: abstract base `PricingProvider` with `store: str` and `quote(items: list[ShoppingListItem]) -> StoreQuote`.
- `mock_provider.py`: deterministic price from a hash of the ingredient name (stable, no randomness) → `unit_price`, `line_total = unit_price * (quantity or 1)`.
- `pricing_service.quote_all(items, providers)`: skip items with `source != "supermarket"`, call each provider, return `list[StoreQuote]`.

**Step 4:** PASS, flake8 clean. **Step 5:** Stage.

---

## Phase 2 — Adapters, API, seed

### Task 8: Repository ports + Mongo adapters

**Files:**
- Create: `backend/app/ports/recipe_repo.py`, `menu_repo.py`
- Create: `backend/app/adapters/db/__init__.py`, `mongo_recipe_repo.py`, `mongo_menu_repo.py`
- Test: `backend/tests/test_mongo_repos.py` (using `mongomock-motor`)

**Step 1 (test first):** with a `mongomock_motor.AsyncMongoMockClient`, insert a recipe via `MongoRecipeRepo.create`, read it back via `get`, and assert round-trip equality; upsert a `WeekMenu` via `MongoMenuRepo.save`/`load`.

**Step 2:** FAIL. **Step 3:** Implement abstract ports (`RecipeRepo`, `MenuRepo`) and Motor-based adapters mapping Pydantic ↔ Mongo docs (`_id` ↔ `id`). `MenuRepo.load` returns an empty `WeekMenu` when absent; `save` upserts `_id="current"`. **Step 4:** PASS, flake8 clean. **Step 5:** Stage.

---

### Task 9: Seed data — Recipe 1

**Files:**
- Create: `backend/app/seed.py`
- Test: `backend/tests/test_seed.py`

**Step 1 (test first):** `build_seed_recipe()` returns a `Recipe` with `servings == 4`, `icon == "🍝"`, `>= 9` steps, a `prep` step present, and specific ingredient checks (`macaroni` 350 g; `gehakt` 300 g with `notes`/`source`).

**Step 2:** FAIL. **Step 3:** Implement `build_seed_recipe()` transcribing Recipe 1 faithfully:
- Groups: Pasta, Basis, Tomatenbasis, Kruiden, Frisse afwerking — quantities/units from the source (350 g macaroni; 300 g gehakt; 1 ui; 2–3 knoflook; 1 rode paprika; 1 courgette; 400 g tomatenblokjes; 200 g passata; 1 el tomatenpuree; 0.5 tl venkelzaad; 1 tl oregano; 0.25 tl chilivlokken; 1 laurierblad; zout/peper; rasp 1 citroen; sap ⅓–½ citroen; basilicum; 35 g Parmezaan; 2 el olijfolie; ½ kop pastawater).
- Steps 1–9 with `phase` and duration ranges from the source, `instructions` holding the **full elaborate text including reasoning**. Prepend a synthetic step 0 `phase="prep"` "Mise en place" (~10 min) with a note that it is an estimate.
- `notes="Gehakt zonder zout."`; gehakt ingredient `source="external"` reserved (still shown; excluded from store totals later).
- Add `seed_if_empty(repo)` that inserts it when the collection is empty.

**Step 4:** PASS, flake8 clean. **Step 5:** Stage.

---

### Task 10: API schemas + routers + app wiring

**Files:**
- Create: `backend/app/api/__init__.py`, `api/schemas/__init__.py`, `recipes.py` (DTOs), `menu.py`, `shopping.py`, `pricing.py`
- Create: `backend/app/api/routers/__init__.py`, `recipes.py`, `weekmenu.py`, `shopping.py`, `pricing.py`
- Create: `backend/app/main.py`
- Test: `backend/tests/test_api.py` (httpx `ASGITransport`, mongomock-backed deps)

**Step 1 (test first):** integration tests hitting the ASGI app with a mongomock repo override:
- `GET /recipes` returns the seeded recipe card.
- `GET /recipes/{id}` returns full recipe with steps.
- `POST /recipes` then `GET` round-trips a new recipe; `PUT` updates; `DELETE` removes.
- `PUT /weekmenu/assignments` assigns; a second `PUT` moving to an occupied day swaps; `GET /weekmenu` reflects it.
- `GET /shopping-list` returns scaled/aggregated items.
- `POST /pricing/quote` returns two store quotes with totals.

**Step 2:** FAIL. **Step 3:** Implement:
- Dependency-injected repos/providers via FastAPI `Depends`, overridable in tests.
- Routers delegate to services; **no business logic in routers**.
- `main.py`: create `FastAPI`, CORS allowing `http://localhost:8173`, include routers, `startup` seeds via `seed_if_empty`, `GET /weekmenu` computes the 14-day window from `date.today()`.
- `PUT /weekmenu/assignments` body `{date, recipeId, multiplier}`; if a `fromDate` is provided it's a move/swap, else an assign.

**Step 4:** PASS, flake8 clean. **Step 5:** Stage.

---

## Phase 3 — Frontend (Vue 3 + pnpm)

### Task 11: Frontend scaffold + tooling

**Files:**
- Create: `frontend/package.json`, `pnpm-lock.yaml`, `.npmrc`, `vite.config.ts`, `tsconfig.json`, `index.html`, `src/main.ts`, `src/App.vue`, `src/router.ts`

**Step 1:** `.npmrc` with `minimum-release-age=4320` (3 days, minutes) and `minimum-release-age-exclude=` empty. `package.json` pins Vue 3, vue-router 4, pinia 2, vite 6, typescript 5, vitest 2 (verify each version's release date ≤ 2026-08-14; pnpm's `minimumReleaseAge` enforces it during install).

**Step 2:** `pnpm install` → lockfile written. `vite.config.ts` reads `VITE_API_BASE`. Router with routes `/` (Calendar), `/buy` (Buy), `/recipe/:id` (Detail), `/recipe/:id/edit` and `/recipe/new` (Edit).

**Step 3:** Run `pnpm vitest run` (no tests yet) → passes trivially. Stage all.

---

### Task 12: API client + menu store (with unit tests)

**Files:**
- Create: `frontend/src/api/client.ts`
- Create: `frontend/src/stores/menu.ts`
- Test: `frontend/tests/menu.store.test.ts`

**Step 1 (test first, Vitest):** test the store's local swap/move resolution and multiplier update mirror the backend semantics (move to empty, swap when occupied) so the UI is optimistic and correct before the server round-trip.

**Step 2:** FAIL. **Step 3:** Implement `client.ts` (typed fetch wrappers for every endpoint) and a Pinia `menu` store holding `assignments`, `recipes`, `shoppingList`, with actions `assign`, `moveOrSwap`, `setMultiplier`, `refreshShoppingList` — each calls the API then updates state. **Step 4:** `pnpm vitest run` PASS. **Step 5:** Stage.

---

### Task 13: CalendarView + drag/drop + portions + shopping panel

**Files:**
- Create: `frontend/src/views/CalendarView.vue`
- Create: `frontend/src/components/RecipeCard.vue`, `DayCell.vue`, `PortionSelector.vue`, `ShoppingList.vue`

**Step 1:** Build the 14-day grid from today. Native HTML5 DnD: `RecipeCard` sets `dataTransfer` recipeId; `DayCell` handles `dragover`/`drop`; dragging between cells carries the source date → store `moveOrSwap`. `PortionSelector` (0.5/1/1.5/2 + custom) calls `setMultiplier`. `ShoppingList` panel binds `store.shoppingList`. Header has **Save** (confirmation toast) and **Buy** (`router.push('/buy')`) plus **Add recipe** (`/recipe/new`). Clicking a card/cell recipe → `/recipe/:id`.

**Step 2:** Manual check via `pnpm dev` (covered end-to-end in Task 15). Stage.

---

### Task 14: RecipeDetailView + RecipeEditView + BuyView

**Files:**
- Create: `frontend/src/views/RecipeDetailView.vue`, `RecipeEditView.vue`, `BuyView.vue`

**Step 1:** `RecipeDetailView` fixed layout order: icon+title → **full ingredient list first** (grouped) → **cook-time header** (total + prep-vs-active-cook summary computed from step phases/durations) → steps with per-step times and full instructions. `RecipeEditView` edits title, icon, servings, grouped ingredients (name/quantity/unit), steps; includes save (POST/PUT) and delete (DELETE). `BuyView` calls `POST /pricing/quote`, renders per-store tables with totals, highlights the cheapest store. Stage.

---

## Phase 4 — Integration & finish

### Task 15: End-to-end bring-up

**Step 1:** `make build` → all three images build. If a pin is rejected by freshness tooling, bump down to the newest ≤ 2026-08-14 release and re-lock.

**Step 2:** `make up`; `make ps` shows mongo/api/frontend healthy.

**Step 3:** Verify:
- `curl -s http://localhost:18420/recipes` → seeded Macaroni recipe.
- Open `http://localhost:8173` → drag recipe onto a day; change multiplier to 2×; confirm shopping list shows 700 g macaroni; drag between days to swap; open recipe detail; open Buy page and confirm two store totals with cheapest highlighted.
- Confirm Mongo reachable on host: `mongosh "mongodb://localhost:47017/basket" --eval "db.recipes.countDocuments()"` → ≥ 1.

**Step 4:** `make test-backend` → pytest green + flake8 clean.

**Step 5:** Update `README.md` with run instructions (`make build && make up`), ports, and the v0.1 vs later scope. Stage README + any fixes.

---

### Task 16: Single final commit

**Step 1:** Confirm clean quality gates: `cd backend && uv run pytest -v && uv run flake8 app tests`; `cd frontend && pnpm vitest run`.

**Step 2:** Verify branch: if on `main`, create a feature branch first (`git checkout -b feat/basket-v01`).

**Step 3:** Stage everything including the design and this plan:

```bash
git add -A
git status   # review
```

**Step 4:** One commit (per user rule; no AI mentions):

```bash
git commit -m "feat: basket v0.1 - containerized menu planner with calendar, shopping list and mock pricing"
```

---

## Task dependency notes

- Phase 1 (Tasks 4–7) is pure and can be built/tested without Mongo or Docker.
- Tasks 8–10 depend on Phase 1. Task 9 seed depends on Task 4 entities.
- Phase 3 (11–14) depends only on the API contract (Task 10), not its internals.
- Task 15 requires all prior tasks. Task 16 is last (single commit rule).

## Verification checklist (before claiming done)

- [ ] `uv run pytest` green; `uv run flake8 app tests` clean.
- [ ] `pnpm vitest run` green.
- [ ] `make build && make up` succeed; all containers healthy.
- [ ] Drag/drop assign, swap, and 2× scaling verified in the browser.
- [ ] Buy page shows per-store totals with cheapest highlighted.
- [ ] Mongo (47017) and API (18420) reachable from host.
- [ ] Exactly one commit, on a feature branch, no AI mentions in the message.
