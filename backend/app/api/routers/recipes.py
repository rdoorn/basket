"""Recipe endpoints.

The router only parses requests, delegates to the repository, and shapes
responses. No business logic lives here.
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.api.deps import get_recipe_repo
from app.api.schemas.recipes import RecipeCard, RecipeInput
from app.domain.recipe import Recipe
from app.ports.recipe_repo import RecipeRepo

router = APIRouter(prefix="/recipes", tags=["recipes"])


@router.get("", response_model=list[RecipeCard])
async def list_recipes(repo: RecipeRepo = Depends(get_recipe_repo)) -> list[RecipeCard]:
    """Return every recipe as a trimmed library card."""
    recipes = await repo.list()
    return [RecipeCard.from_recipe(recipe) for recipe in recipes]


@router.get("/{recipe_id}", response_model=Recipe)
async def get_recipe(
    recipe_id: str, repo: RecipeRepo = Depends(get_recipe_repo)
) -> Recipe:
    """Return the full recipe for ``recipe_id`` (404 when missing)."""
    recipe = await repo.get(recipe_id)
    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe


@router.post("", response_model=Recipe, status_code=status.HTTP_201_CREATED)
async def create_recipe(
    body: RecipeInput, repo: RecipeRepo = Depends(get_recipe_repo)
) -> Recipe:
    """Create a recipe, assigning a server-side id when none is supplied."""
    recipe_id = body.id or uuid.uuid4().hex
    recipe = body.to_recipe(recipe_id)
    return await repo.create(recipe)


@router.put("/{recipe_id}", response_model=Recipe)
async def update_recipe(
    recipe_id: str,
    body: RecipeInput,
    repo: RecipeRepo = Depends(get_recipe_repo),
) -> Recipe:
    """Update the recipe at ``recipe_id`` (404 when missing)."""
    updated = await repo.update(recipe_id, body.to_recipe(recipe_id))
    if updated is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return updated


@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recipe(
    recipe_id: str, repo: RecipeRepo = Depends(get_recipe_repo)
) -> Response:
    """Delete the recipe at ``recipe_id`` (404 when missing)."""
    if not await repo.delete(recipe_id):
        raise HTTPException(status_code=404, detail="Recipe not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
