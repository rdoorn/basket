# Leftovers + editable staple/pet lists — Design

Date: 2026-08-19
Status: **Approved** — ready for implementation planning.
Builds on: `2026-08-19-bakes-and-pet-food-design.md` (pet food, extras), `2026-08-17-basket-v01-design.md` (ports & adapters).

## 1. Purpose

Four refinements:

1. **Leftovers feed the cavias.** A recipe ingredient that is also a pet food is bought once
   (in the shopping list); 50% of its standard weight counts toward the pet's weekly target,
   and it is not bought again as dedicated pet food.
2. **Editable "heb ik vast wel" list** — move staples from a hardcoded set to a database
   collection with a management page.
3. **Editable pet-food list page** — a dedicated page to curate foods + standard weights.
4. **Recipe fix** — "melk óf ei" glaze becomes plain "melk".

## 2. Leftovers (recipe/pet overlap)

### Rule
- Match by normalized name (`normalize_name`: trim + lower). A pet food whose name appears in
  the current recipe-derived shopping list is an **overlap**.
- **Coverage**: `covered_g = Σ round(0.5 * weight_g)` over overlapping pet foods (per the pet
  food's standard weight, not the recipe amount — chosen for robustness given mixed units).
- **Effective fill target**: `max(0, pet_target_g - covered_g)`.
- **Pick pool**: dedicated pet selection is drawn from pet foods **excluding** overlaps
  (leftovers already feed them).
- **Dedup**: overlapping foods appear only under **Boodschappen** (recipe line), never under
  **Huisdiervoer**. This is enforced at the shopping-breakdown level too, so a stale
  `pet_selection` entry that later becomes a recipe ingredient is suppressed.

### Where it lives
- `pet_service` stays pure. `generate`/`adjust` take an `exclude_names: set[str]` (the recipe
  overlap) and use the effective target internally via a `coverage_g(foods, names)` helper.
- The pet router builds the recipe-ingredient name set from the shopping service (recipe items
  only, group is None), normalizes it, and passes it in. It also returns `coveredG` on `PetOut`
  so the panel can show "≈ 1 kg (~200 g uit restjes)".
- The shopping breakdown suppresses a pet-selection line whose normalized name is already a
  recipe item.

## 3. Editable staples ("heb ik vast wel")

- New collection **`staples`**: `{ _id, name }` (name stored normalized). Seeded once (if empty)
  with the current defaults **plus** `suiker, zwarte sesam, instant gist, basterdsuiker`:
  `olijfolie, citroensap, chilivlokken, gehakt, rundergehakt, zout, zwarte peper, venkelzaad,
  suiker, zwarte sesam, instant gist, basterdsuiker`.
- `app/domain/staples.py`: keep `normalize_name`; replace the module constant / `is_staple(name)`
  with `is_staple(name, staples: set[str])`. The staple set is loaded from the repo and threaded
  into `shopping_service.partition_items` / `build_breakdown`.
- New port `StapleRepo` + Mongo adapter (`list`, `create`, `delete`, `count`); `seed_staples_if_empty`.
- API: `GET /staples`, `POST /staples {name}`, `DELETE /staples/{id}`.
- Page **`/staples`**: list + add (name) + remove.

## 4. Pet-food list page + new foods

- Existing `pet_foods` collection/repo/CRUD stays. Add a dedicated page **`/pet-foods`** (route +
  nav link) wrapping the editor (name + standard weight in grams).
- Seed adds `koolrabi (300 g), mais (vers) (250 g), witlof (150 g), babyromaine (200 g)` to the
  existing paprika/komkommer/ijsbergsla/wortel/andijvie/veldsla.

## 5. Recipe fix

- In `build_dierbroodjes`, the glaze ingredient becomes a single `melk` line (drop the "óf ei"
  alternative). Only occurrence of "melk of ei" today.

## 6. Data model summary

- New: `staples` collection `{ _id, name }`.
- `pet_foods` unchanged; seed extended.
- `weekmenu` unchanged (`pet_selection`, `pet_target_g`, `extras`, `assignments`, `item_choices`).
- `ShoppingListItem` unchanged (`group` already exists).

## 7. API changes

- `GET/POST/DELETE /staples`.
- `PetOut` gains `coveredG` (leftover coverage for the current menu).
- Pet mutation endpoints (`/pet`, `/pet/regenerate`, `/pet/target`, `/pet/replace`) now also read
  recipes to compute the overlap; behaviour otherwise unchanged.
- Shopping/pricing: partition now takes the staple set from the repo; pet-line dedup vs recipe items.

## 8. Frontend

- Router: add `/staples` and `/pet-foods` routes; nav links in `App.vue`.
- `StaplesView.vue` (list/add/remove via `/staples`); `PetFoodsView.vue` (wraps `PetFoodEditor`).
- Store: `staples` state + `loadStaples`/`addStaple`/`deleteStaple`; `PetPanel` shows `coveredG`.
- The "heb ik vast wel" pantry panel is unchanged in behaviour (data now comes from the DB).

## 9. Architecture

- Ports & adapters preserved: new `StapleRepo` port + Mongo adapter; `is_staple` becomes a pure
  function over an injected set; `pet_service` stays pure (coverage/exclude are pure inputs);
  routers thin. Pricing/cheapest still behind the pricing port.

## 10. Testing

- **Backend:** `coverage_g` + `generate`/`adjust` with `exclude_names` (deterministic RNG);
  breakdown dedup (pet line suppressed when it's a recipe item); staple repo round-trip + seed;
  `partition_items` with an injected staple set (incl. added `suiker` etc.); pet router overlap
  (a salad with ijsbergsla reduces the pet target and drops ijsbergsla from Huisdiervoer); staples
  API; bread glaze == "melk".
- **Frontend:** store actions for staples; `PetPanel` renders `coveredG`.
- Verify end-to-end in containers.

## 11. Later (not built)
- Ingredient alias engine (general "X of Y" normalization) — only the bread glaze needed it now.
- Per-store real weights/prices when a store adapter exists.
