"""Recipe request/response DTOs.

``RecipeCard`` is the trimmed list representation; recipe create/update accept
a full recipe body without a client-supplied id (the server owns ids). Full
recipe responses reuse the domain :class:`Recipe` directly.
"""
from typing import Literal

from pydantic import BaseModel, Field

from app.domain.recipe import Ingredient, Recipe, Step


class RecipeCard(BaseModel):
    """Trimmed recipe representation for library cards."""

    id: str
    title: str
    icon: str
    description: str = ""
    category: Literal["meal", "bake"] = "meal"

    @classmethod
    def from_recipe(cls, recipe: Recipe) -> "RecipeCard":
        """Build a card from a full :class:`Recipe`."""
        return cls(
            id=recipe.id,
            title=recipe.title,
            icon=recipe.icon,
            description=recipe.description,
            category=recipe.category,
        )


class RecipeInput(BaseModel):
    """Body for creating or updating a recipe (server assigns the id)."""

    id: str | None = None
    title: str
    icon: str
    description: str = ""
    servings: int
    category: Literal["meal", "bake"] = "meal"
    total_time_min_low: int | None = None
    total_time_min_high: int | None = None
    tags: list[str] = Field(default_factory=list)
    notes: str | None = None
    ingredients: list[Ingredient] = Field(default_factory=list)
    steps: list[Step] = Field(default_factory=list)

    def to_recipe(self, recipe_id: str) -> Recipe:
        """Return a domain :class:`Recipe` with the given ``recipe_id``."""
        data = self.model_dump()
        data["id"] = recipe_id
        return Recipe.model_validate(data)
