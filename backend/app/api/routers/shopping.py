"""Shopping-list endpoint.

Loads the current menu and all recipes, then delegates aggregation and scaling
to ``shopping_service``.
"""
from fastapi import APIRouter, Depends

from app.api.deps import get_menu_repo, get_recipe_repo
from app.api.schemas.shopping import ShoppingListOut
from app.ports.menu_repo import MenuRepo
from app.ports.recipe_repo import RecipeRepo
from app.services import shopping_service

router = APIRouter(prefix="/shopping-list", tags=["shopping"])


@router.get("", response_model=ShoppingListOut)
async def get_shopping_list(
    menu_repo: MenuRepo = Depends(get_menu_repo),
    recipe_repo: RecipeRepo = Depends(get_recipe_repo),
) -> ShoppingListOut:
    """Return the aggregated, scaled shopping list for the current menu."""
    menu = await menu_repo.load()
    recipes = await recipe_repo.list()
    recipes_by_id = {recipe.id: recipe for recipe in recipes}
    items = shopping_service.build_shopping_list(menu, recipes_by_id)
    return ShoppingListOut.from_items(items)
