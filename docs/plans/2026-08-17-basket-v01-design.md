# Basket v0.1 — Design

Date: 2026-08-17
Status: **Approved** — ready for implementation planning.

## 1. Purpose

A no-login web app that lets you plan a two-week menu by dragging recipes onto a
calendar, automatically builds a shopping list from the planned recipes (scaled to the
number of eaters), and (later) compares prices across supermarkets to find the cheapest
place to buy. v0.1 delivers the full app with a **mock** pricing adapter; real store
integrations come later behind the same port.

## 2. Scope

### In scope (v0.1 — build now)
- Container setup: `docker-compose.yml` + `Makefile` to build and run everything.
- MongoDB (persistent), FastAPI backend, Vue 3 frontend — all in containers.
- Recipe library with one seeded recipe (Macaroni alla Siciliana), plus add / edit /
  delete recipes.
- Read-only recipe detail page (icon, full ingredient list, cook-time header, elaborate
  steps with per-step times).
- 14-day calendar (today + next 13 days). Drag recipe → day (assign); drag day → day
  (swap if occupied, move if empty).
- Per-assignment portion **multiplier** (0.5× / 1× / 1.5× / 2× / custom), relative to the
  recipe's base servings.
- Shopping list **derived** from the current menu, aggregated across recipes and scaled by
  each assignment's multiplier.
- Auto-save on every calendar change; explicit **Save** button = confirmation snapshot.
- **Buy** page: aggregated ingredients with per-store price and total-per-store, cheapest
  highlighted — powered by the mock pricing adapter.

### Out of scope (documented for later)
- Real Albert Heijn / Picnic adapters (credentials, live scraping/API).
- Ingredient **brand override / pinning** (e.g. `spaghetti` → `Grand'Italia spaghetti`),
  including the "unavailable → resolve" prompt.
- **External-source** ingredients (e.g. farm `gehakt`) excluded from store totals with a
  "vriezer of kopen?" prompt.
- Season-aware menu auto-generation (from the original concept).
- Authentication / multi-user.

## 3. Constraints

- **Dependency freshness:** do not use any library/tool release newer than **3 days**.
  Enforced with uv `exclude-newer` (backend) and pnpm `minimumReleaseAge` (frontend);
  all versions pinned. (Supersedes the README's 7-day note.)
- **Tooling:** backend managed by `uv`; frontend by `pnpm`.
- **No login** on the website; data persisted in MongoDB.
- **Non-obvious host ports**, all reachable from the host:
  - MongoDB `47017`, API `18420`, Frontend `8173`.
- **Python quality:** PEP 8/257/484/561/20; flake8 static analysis; pytest.

## 4. Architecture — ports & adapters (hexagonal)

Vue → REST/JSON → FastAPI routers → services (business logic) → ports (abstract
interfaces) → adapters (Mongo, pricing). Stores (AH/Picnic) and the DB are **adapters**;
the domain never imports a framework or a vendor.

```
basket/
  docker-compose.yml
  Makefile
  backend/
    pyproject.toml              # uv, exclude-newer pin, flake8 config
    app/
      main.py                   # FastAPI app, router wiring, startup seed
      config.py                 # env: mongo URL, ports, freshness date
      domain/                   # pure entities, no framework imports
        recipe.py               # Recipe, Ingredient, Step
        menu.py                 # WeekMenu, DayAssignment
        shopping.py             # ShoppingListItem
        pricing.py              # PricedItem, StoreQuote
      services/
        menu_service.py         # assign / move / swap resolution
        shopping_service.py     # aggregate + scale -> shopping list
        pricing_service.py      # run list through pricing port -> totals
      ports/
        recipe_repo.py          # abstract repository interfaces
        menu_repo.py
        pricing_provider.py     # abstract: quote(items) -> StoreQuote
      adapters/
        db/
          mongo_recipe_repo.py
          mongo_menu_repo.py
        pricing/
          mock_provider.py      # deterministic fake prices (v0.1)
          # albert_heijn.py, picnic.py   <- later, same port
      api/
        routers/                # recipes, weekmenu, shopping, pricing
        schemas/                # pydantic request/response DTOs
    tests/                      # pytest; fake in-memory repos + mock provider
  frontend/
    package.json                # pnpm, minimumReleaseAge, pinned deps
    src/
      main.ts
      api/client.ts
      stores/menu.ts            # Pinia: assignments, multipliers
      views/
        CalendarView.vue
        BuyView.vue
        RecipeDetailView.vue
        RecipeEditView.vue
      components/
        RecipeCard.vue
        DayCell.vue
        ShoppingList.vue
        PortionSelector.vue
    tests/                      # Vitest: swap/move + scaling logic
```

## 5. Data model (MongoDB)

### `recipes`
```jsonc
{
  "_id": "<id>",
  "title": "Macaroni alla Siciliana (frisse variant, zonder olijven)",
  "icon": "🍝",
  "description": "Lichter, frisser, aromatischer, maar nog steeds stevig en vullend.",
  "servings": 4,
  "total_time_min_low": 50,
  "total_time_min_high": 60,
  "tags": ["pasta", "zomer"],
  "notes": "Gehakt zonder zout.",
  "ingredients": [
    {
      "group": "Pasta",
      "name": "macaroni",
      "quantity": 350, "unit": "g", "note": null,
      // reserved for later, nullable in v0.1:
      "normalized_name": null, "brand_override": null, "source": "supermarket"
    }
    // ... Basis, Tomatenbasis, Kruiden, Frisse afwerking groups
  ],
  "steps": [
    {
      "order": 1,
      "title": "Gehakt bruin bakken",
      "phase": "cook",              // prep | cook | finish
      "duration_min_low": 8,
      "duration_min_high": 10,
      "instructions": "Gebruik 300 g gehakt, 1 el olijfolie, ½ tl zout, zwarte peper. Bak op middelhoog tot hoog vuur. Belangrijk: eerst laten liggen, goed laten bruinen, randjes donker laten worden. Doel: veel smaak opbouwen."
    }
    // ... full elaborate instructions preserved verbatim per step
  ]
}
```
- `instructions` preserves the complete original text **including reasoning**; nothing is
  summarized away.
- `normalized_name`, `brand_override`, `source` exist now (nullable/defaulted) so the later
  override/sourcing features need no migration.

### `weekmenu` (single document)
```jsonc
{
  "_id": "current",
  "assignments": {
    "2026-08-17": { "recipeId": "<id>", "multiplier": 1.0 },
    "2026-08-18": { "recipeId": "<id>", "multiplier": 2.0 }
  }
}
```
- Auto-saved on every change. One recipe per day in v0.1.

### Derived (not stored)
- **Shopping list:** computed from `weekmenu` — for each assignment, every ingredient
  quantity × multiplier, aggregated by `(normalized name, unit)`.
- **Pricing quotes:** computed on demand by `pricing_service` via the pricing port.

## 6. API endpoints

- `GET /recipes` — list (card data: id, title, icon).
- `GET /recipes/{id}` — full recipe for the detail page.
- `POST /recipes` — create.
- `PUT /recipes/{id}` — update (title, servings, ingredients, steps, icon…).
- `DELETE /recipes/{id}` — delete.
- `GET /weekmenu` — 14-day window from today with resolved assignments.
- `PUT /weekmenu/assignments` — body `{date, recipeId, multiplier}`. Server resolves:
  assign to empty day, or move/swap when dragging between days.
- `DELETE /weekmenu/assignments/{date}` — clear a day.
- `GET /shopping-list` — aggregated + scaled list from the current menu.
- `POST /pricing/quote` — runs the shopping list through pricing providers → per-store
  totals; backs the Buy page.

## 7. Frontend behaviour

### CalendarView
- Left: recipe library (draggable `RecipeCard`s; click a card → detail view).
- Right: 14 `DayCell`s (today + 13). Native HTML5 drag-and-drop:
  - recipe → day = assign;
  - day → day = swap if target occupied, else move.
- Each occupied cell shows a `PortionSelector` (0.5× / 1× / 1.5× / 2× / custom). Clicking
  the recipe in a cell → detail view.
- Every change calls the API (auto-save) and refreshes the live `ShoppingList` panel.
- **Save** button → confirmation toast/snapshot. **Buy** button → BuyView.
- **Add recipe** button → RecipeEditView (blank).

### RecipeDetailView (read-only) — fixed layout order
1. Food **icon** + title (+ short description).
2. **Full ingredient list first**, grouped, with quantities/units.
3. **Cook-time header:** total time + prep-vs-active-cook summary computed from step
   `phase`/durations.
4. **Steps** in order, each with its time range and full elaborate instructions.
- Reachable by clicking any recipe (library card or calendar cell).

### RecipeEditView (add/edit)
- Edit title, icon, servings/people, grouped ingredients (name, quantity, unit —
  g/el/tl/stuks/…), and steps (title, phase, duration, instructions).
- Changing `servings` re-bases the recipe; calendar multipliers stay relative to the new
  base.
- Includes delete.

### BuyView
- Table of aggregated ingredients with per-store price and total-per-store, cheapest
  highlighted. Mock pricing adapter in v0.1.

## 8. Seed data

On startup, if `recipes` is empty, seed **Recipe 1 — Macaroni alla Siciliana** with:
- `icon: "🍝"`, `servings: 4`, total 50–60 min, note "gehakt zonder zout".
- Grouped ingredients (Pasta / Basis / Tomatenbasis / Kruiden / Frisse afwerking) with
  quantities and units from the source.
- Nine steps with `phase` (prep/cook/finish), duration ranges, and full instructions. A
  synthetic `prep` step (~10 min mise en place) is added and marked as an estimate the
  user can adjust.

## 9. Testing

- **Backend (pytest + flake8):** unit tests for `menu_service` (assign/move/swap),
  `shopping_service` (aggregation + multiplier scaling), and `pricing_service` (against the
  mock provider), using fake in-memory repositories. flake8 must pass.
- **Frontend (Vitest):** the Pinia store's swap/move resolution and multiplier scaling.

## 10. Ports & adapters summary

| Concern        | Port                | v0.1 adapter        | Later                     |
|----------------|---------------------|---------------------|---------------------------|
| Recipe storage | `recipe_repo`       | `mongo_recipe_repo` | —                         |
| Menu storage   | `menu_repo`         | `mongo_menu_repo`   | —                         |
| Pricing        | `pricing_provider`  | `mock_provider`     | `albert_heijn`, `picnic`  |

## 11. Future extensions (reserved, not built)

- Real AH/Picnic pricing adapters (credentials, scraping/API).
- Ingredient brand override/pinning + "unavailable → buy alt / don't buy / change recipe".
- External-source ingredients (farm gehakt) excluded from totals + "vriezer of kopen?"
  prompt.
- Season-aware automatic weekmenu generation.
- Photo upload / proper icon set for recipes.
