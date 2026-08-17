"""Shopping-list endpoints.

Loads the current menu and all recipes, then delegates aggregation, scaling and
the staple split to ``shopping_service``. The staple endpoint promotes or
un-promotes a "heb ik vast wel" ingredient and persists the choice on the menu.
"""
from fastapi import APIRouter, Depends

from app.api.deps import get_menu_repo, get_recipe_repo
from app.api.schemas.shopping import ShoppingListOut, StapleToggleIn
from app.ports.menu_repo import MenuRepo
from app.ports.recipe_repo import RecipeRepo
from app.services import shopping_service

router = APIRouter(prefix="/shopping-list", tags=["shopping"])


async def _breakdown(menu_repo: MenuRepo, recipe_repo: RecipeRepo) -> ShoppingListOut:
    """Build the current shopping-list breakdown response."""
    menu = await menu_repo.load()
    recipes = await recipe_repo.list()
    recipes_by_id = {recipe.id: recipe for recipe in recipes}
    breakdown = shopping_service.build_breakdown(menu, recipes_by_id)
    return ShoppingListOut.from_breakdown(breakdown)


@router.get("", response_model=ShoppingListOut)
async def get_shopping_list(
    menu_repo: MenuRepo = Depends(get_menu_repo),
    recipe_repo: RecipeRepo = Depends(get_recipe_repo),
) -> ShoppingListOut:
    """Return the shopping list plus the "heb ik vast wel" pantry list."""
    return await _breakdown(menu_repo, recipe_repo)


@router.put("/staple", response_model=ShoppingListOut)
async def set_staple(
    body: StapleToggleIn,
    menu_repo: MenuRepo = Depends(get_menu_repo),
    recipe_repo: RecipeRepo = Depends(get_recipe_repo),
) -> ShoppingListOut:
    """Promote or un-promote a staple and return the updated breakdown."""
    menu = await menu_repo.load()
    menu.set_staple_buy(body.name, body.buy)
    await menu_repo.save(menu)
    return await _breakdown(menu_repo, recipe_repo)
