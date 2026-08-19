"""Shopping-list endpoints.

Loads the current menu and all recipes, then delegates aggregation, scaling and
the pantry split to ``shopping_service``. The item endpoint moves an ingredient
between the shopping list and the "heb ik vast wel" list and persists the choice
on the menu.
"""
from fastapi import APIRouter, Depends

from app.api.deps import get_menu_repo, get_recipe_repo
from app.api.schemas.shopping import ItemBuyIn, ShoppingListOut
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


@router.put("/item", response_model=ShoppingListOut)
async def set_item_buy(
    body: ItemBuyIn,
    menu_repo: MenuRepo = Depends(get_menu_repo),
    recipe_repo: RecipeRepo = Depends(get_recipe_repo),
) -> ShoppingListOut:
    """Move an ingredient between the two lists and return the updated split."""
    menu = await menu_repo.load()
    menu.set_item_buy(body.name, body.buy)
    await menu_repo.save(menu)
    return await _breakdown(menu_repo, recipe_repo)
