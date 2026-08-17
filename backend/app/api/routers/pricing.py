"""Pricing endpoint.

Builds the current shopping list and runs it through the configured pricing
providers via ``pricing_service``.
"""
from fastapi import APIRouter, Depends

from app.api.deps import get_menu_repo, get_pricing_providers, get_recipe_repo
from app.api.schemas.pricing import PricingOut
from app.ports.menu_repo import MenuRepo
from app.ports.pricing_provider import PricingProvider
from app.ports.recipe_repo import RecipeRepo
from app.services import pricing_service, shopping_service

router = APIRouter(prefix="/pricing", tags=["pricing"])


@router.post("/quote", response_model=PricingOut)
async def quote(
    menu_repo: MenuRepo = Depends(get_menu_repo),
    recipe_repo: RecipeRepo = Depends(get_recipe_repo),
    providers: list[PricingProvider] = Depends(get_pricing_providers),
) -> PricingOut:
    """Return per-store quotes for the current shopping list."""
    menu = await menu_repo.load()
    recipes = await recipe_repo.list()
    recipes_by_id = {recipe.id: recipe for recipe in recipes}
    items = shopping_service.build_shopping_list(menu, recipes_by_id)
    quotes = pricing_service.quote_all(items, providers)
    return PricingOut.from_quotes(quotes)
