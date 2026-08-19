# Bake recipes + Pet food — Design

Date: 2026-08-19
Status: **Approved** — ready for implementation planning.
Builds on: `2026-08-17-basket-v01-design.md` (ports & adapters, MongoDB, Vue calendar).

## 1. Purpose

Two additions to the Basket planner:

1. **Bake recipes** (bread, cookies) — recipes that are not tied to a calendar day
   but whose ingredients still belong in the shopping bag. Dragged into a separate
   **"Extra's"** zone beside the day grid.
2. **Pet food** — a generic (not cavia-specific) weekly pet-food generator. From an
   editable list of foods the pet likes, auto-select a mix (cheapest + random) that
   fills a weekly weight target; each pick can be re-rolled. Selected foods join the
   shopping bag and are priced on the Buy page.

## 2. Feature A — Bake recipes + "Extra's" zone

### Model
- `Recipe` gains `category: "meal" | "bake"` (default `"meal"`).
- `WeekMenu` gains `extras: list[ExtraAssignment]` where
  `ExtraAssignment = { recipe_id, multiplier }` — recipes in the bag without a date.

### Behaviour
- Calendar page shows an **"Extra's"** drop zone next to the 14-day grid. Dragging any
  recipe there appends an extra (default multiplier 1×). Bakes are labelled 🍞 in the
  library and are the natural fit, but any recipe may be added.
- Extras carry the same **×multiplier** control as day assignments (2× = double batch).
- Removing an extra clears it from the bag.
- Shopping aggregation (`build_shopping_list`) folds extras in alongside day
  assignments — each extra's ingredients scaled by its multiplier.

### Seed
- Add **"Zachte Dierbroodjes (Japanse/Koreaanse stijl)"** as `category: "bake"`, icon 🍞,
  servings 8, with the full elaborate steps (mengen → kneden → boter → uitkneden →
  koelen → verdelen → vormen → tweede rijs → decoreren → bakken), per-step times, and the
  notes (broodmeel volgende keer, vingertest, 93–95 °C kern, niet direct opensnijden).
  Ingredient groups: Deeg / Decoratie / Glans.

## 3. Feature B — Pet food (weight-driven, generic)

### Model
- New collection **`pet_foods`**, seeded and editable. Each:
  `{ _id, name, weight_g }` where `weight_g` is a **static guess** of grams per
  purchase-unit (the store won't tell us up front). Seeds (cavia-friendly, editable):
  paprika 150, komkommer 400, ijsbergsla 400, wortel 80, andijvie 300, veldsla 100.
- `WeekMenu` gains:
  - `pet_target_g: int` (default **1000**),
  - `pet_selection: list[str]` (names of currently chosen foods).

### Selection (`pet_service`, uses the pricing port)
- **Fill to weight**: start with the **1 cheapest** food (priced via the pricing
  provider), then add **random** distinct foods until the summed guessed `weight_g`
  reaches `pet_target_g` (cap iterations at the list size so a short list can't loop).
- **Weight is a guide, shown as a total only** — the UI shows "Huisdiervoer ≈ 1 kg",
  never per-item grams.
- **± 250 g** buttons adjust `pet_target_g` (floor 0). Adjusting **adds/removes** foods
  to re-approach the target while keeping existing picks where possible (grow: add random
  until reached; shrink: drop trailing random picks, keep the cheapest anchor).
- **Replace (↻)** on a food swaps just that one for a random food **not** currently
  selected (1:1); the total may drift slightly — acceptable since it is only a guide.
  No available replacement → no-op.
- Randomness lives in the service and is **injectable** (a `random.Random` / seed
  parameter) so tests are deterministic.

### Shopping bag / pricing
- Selected pet foods appear in the shopping breakdown under a **"Huisdiervoer"** group
  and are priced on the Buy page (as count-unit items via the mock provider).
- They are **not** staples and do not participate in the "heb ik vast wel" split.

### Scope
- **One pet** (single food list + one weekly target), generically named. Multiple pets
  side by side (a `pets` collection) is a documented later extension, not built now.

## 4. Data model summary (MongoDB)

- `recipes`: + `category`.
- `weekmenu` (single doc): + `extras`, `pet_target_g`, `pet_selection`
  (existing: `assignments`, `item_choices`).
- `pet_foods`: new collection `{ _id, name, weight_g }`.

## 5. API changes

- `PUT /weekmenu/extras` — body `{ recipeId, multiplier }` append/update an extra;
  `DELETE /weekmenu/extras/{recipeId}` remove one. `GET /weekmenu` returns `extras`.
- `GET /pet/foods`, `POST /pet/foods`, `DELETE /pet/foods/{id}` — manage the list.
- `GET /pet` — current `{ target_g, selection: [{name}] }`.
- `PUT /pet/target` — body `{ target_g }` (or `{ delta_g }`), re-approaches the target,
  returns the updated selection.
- `POST /pet/regenerate` — rebuild the selection from scratch.
- `POST /pet/replace` — body `{ name }` re-roll that one pick.
- `GET /shopping-list` and `POST /pricing/quote` now include extras + pet foods; the
  shopping breakdown groups pet foods under "Huisdiervoer".

## 6. Frontend changes

- Recipe library: badge bakes 🍞; `RecipeEditView` gains a category selector.
- `CalendarView`: an **"Extra's"** drop zone (native HTML5 DnD, reusing the
  `RECIPE_MIME` drag type) rendering extra cards with a portion selector and remove.
- New **"Huisdiervoer"** panel: weekly total with **± ¼ kg** buttons, a **Regenereer**
  button, and the selected foods each with a **↻ replace** control. A small editable
  **pet-food list** (add name + guessed grams, remove) — a section or lightweight modal.
- Store (`menu.ts`): `extras`, `petTarget`, `petSelection`, `petFoods` state and the
  matching actions, each calling the API then refreshing the shopping list.

## 7. Architecture

- Ports & adapters preserved. `pet_service` depends on the `pricing_provider` port for
  "cheapest" and takes an injectable RNG. New `pet_food_repo` port + Mongo adapter.
  Routers stay thin; aggregation/selection live in services.

## 8. Testing

- **Backend (pytest + flake8):** extras folding in shopping aggregation; bake seed
  validity; `pet_service` fill-to-weight (deterministic RNG), ± target grow/shrink,
  replace (incl. exhausted-list no-op), cheapest via a fake pricing provider; pet-food
  repo round-trip; API tests for every new endpoint.
- **Frontend (Vitest):** store actions for extras and pet (target ±, regenerate,
  replace) against a mocked client.
- Verify end-to-end in containers (drag a bake into Extra's; generate pet food; both
  appear in the shopping list and on the Buy page).

## 9. Later extensions (not built)

- Multiple pets (`pets` collection, per-pet target + list).
- Real per-unit weights/prices once a store adapter exists (replaces the guesses and the
  mock "cheapest").
- Bake-specific fields (yield count, tin size) if needed.
