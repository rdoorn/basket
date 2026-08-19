"""Pet-food endpoints.

Thin router over the editable ``pet_foods`` list and the weight-driven
selection in ``pet_service``. Each selection mutation loads the menu and the
food list, builds a ``name -> price`` map by quoting the candidate foods once
through the pricing providers, delegates the pure selection to ``pet_service``
with an injected RNG, then persists ``pet_selection``/``pet_target_g`` on the
menu.

Price map policy: each candidate food is quoted (as a single count-unit line)
against every provider and the **cheapest price across providers** is kept, so
"cheapest anchor" reflects the best available store price — mirroring a shopper
picking the cheapest store per item while staying behind the pricing port.
"""
import random

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import (
    get_menu_repo,
    get_pet_food_repo,
    get_pricing_providers,
)
from app.api.schemas.pet import (
    PetFoodIn,
    PetFoodOut,
    PetOut,
    PetReplaceIn,
    PetTargetIn,
)
from app.domain.pet import PetFood
from app.domain.shopping import ShoppingListItem
from app.ports.menu_repo import MenuRepo
from app.ports.pet_food_repo import PetFoodRepo
from app.ports.pricing_provider import PricingProvider
from app.services import pet_service

router = APIRouter(prefix="/pet", tags=["pet"])


def _price_map(
    foods: list[PetFood], providers: list[PricingProvider]
) -> dict[str, float]:
    """Return each food's cheapest price across ``providers``.

    Foods are priced as single count-unit lines (no per-item grams). A food is
    omitted from the map when no provider prices it; ``pet_service.cheapest``
    treats such foods as most expensive.
    """
    items = [ShoppingListItem(name=food.name) for food in foods]
    prices: dict[str, float] = {}
    for provider in providers:
        quote = provider.quote(items)
        for priced in quote.items:
            current = prices.get(priced.name)
            if current is None or priced.line_total < current:
                prices[priced.name] = priced.line_total
    return prices


@router.get("/foods", response_model=list[PetFoodOut])
async def list_foods(
    repo: PetFoodRepo = Depends(get_pet_food_repo),
) -> list[PetFoodOut]:
    """Return the editable pet-food list."""
    foods = await repo.list()
    return [PetFoodOut.from_food(food) for food in foods]


@router.post("/foods", response_model=PetFoodOut)
async def add_food(
    body: PetFoodIn, repo: PetFoodRepo = Depends(get_pet_food_repo)
) -> PetFoodOut:
    """Add a food to the list (id is generated) and return it."""
    created = await repo.create(
        PetFood(id="", name=body.name, weight_g=body.weight_g)
    )
    return PetFoodOut.from_food(created)


@router.delete("/foods/{food_id}", response_model=list[PetFoodOut])
async def delete_food(
    food_id: str,
    repo: PetFoodRepo = Depends(get_pet_food_repo),
    menu_repo: MenuRepo = Depends(get_menu_repo),
) -> list[PetFoodOut]:
    """Delete a food; 404 when it does not exist. Returns the updated list.

    Also drops the deleted food from the current selection so the shopping bag
    and pricing never surface a food that is no longer in the list.
    """
    foods = await repo.list()
    target = next((food for food in foods if food.id == food_id), None)
    if target is None:
        raise HTTPException(status_code=404, detail="pet food not found")
    await repo.delete(food_id)
    menu = await menu_repo.load()
    if target.name in menu.pet_selection:
        menu.pet_selection = [n for n in menu.pet_selection if n != target.name]
        await menu_repo.save(menu)
    remaining = await repo.list()
    return [PetFoodOut.from_food(food) for food in remaining]


@router.get("", response_model=PetOut)
async def get_pet(
    menu_repo: MenuRepo = Depends(get_menu_repo),
    food_repo: PetFoodRepo = Depends(get_pet_food_repo),
) -> PetOut:
    """Return the current weekly target and resolved food selection."""
    menu = await menu_repo.load()
    foods = await food_repo.list()
    return PetOut.build(menu.pet_target_g, menu.pet_selection, foods)


@router.post("/regenerate", response_model=PetOut)
async def regenerate(
    menu_repo: MenuRepo = Depends(get_menu_repo),
    food_repo: PetFoodRepo = Depends(get_pet_food_repo),
    providers: list[PricingProvider] = Depends(get_pricing_providers),
) -> PetOut:
    """Rebuild the selection from scratch for the current target."""
    menu = await menu_repo.load()
    foods = await food_repo.list()
    prices = _price_map(foods, providers)
    menu.pet_selection = pet_service.generate(
        foods, prices, menu.pet_target_g, random.Random()
    )
    await menu_repo.save(menu)
    return PetOut.build(menu.pet_target_g, menu.pet_selection, foods)


@router.put("/target", response_model=PetOut)
async def set_target(
    body: PetTargetIn,
    menu_repo: MenuRepo = Depends(get_menu_repo),
    food_repo: PetFoodRepo = Depends(get_pet_food_repo),
    providers: list[PricingProvider] = Depends(get_pricing_providers),
) -> PetOut:
    """Set the weekly target (floored at 0) and re-approach it."""
    menu = await menu_repo.load()
    foods = await food_repo.list()
    prices = _price_map(foods, providers)
    menu.pet_target_g = max(0, body.target_g)
    menu.pet_selection = pet_service.adjust(
        menu.pet_selection, foods, prices, menu.pet_target_g, random.Random()
    )
    await menu_repo.save(menu)
    return PetOut.build(menu.pet_target_g, menu.pet_selection, foods)


@router.post("/replace", response_model=PetOut)
async def replace(
    body: PetReplaceIn,
    menu_repo: MenuRepo = Depends(get_menu_repo),
    food_repo: PetFoodRepo = Depends(get_pet_food_repo),
) -> PetOut:
    """Re-roll a single selected food for a random unselected one (1:1)."""
    menu = await menu_repo.load()
    foods = await food_repo.list()
    menu.pet_selection = pet_service.replace(
        menu.pet_selection, foods, body.name, random.Random()
    )
    await menu_repo.save(menu)
    return PetOut.build(menu.pet_target_g, menu.pet_selection, foods)
