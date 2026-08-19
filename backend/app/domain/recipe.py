"""Recipe domain entities: Ingredient, Step, Recipe.

These are pure Pydantic v2 models with no framework or persistence
dependencies. Scaling is expressed as a pure operation returning a new
``Ingredient`` rather than mutating in place.
"""
from typing import Literal

from pydantic import BaseModel, Field


class Ingredient(BaseModel):
    """A single recipe ingredient, optionally grouped and quantified.

    ``normalized_name``, ``brand_override`` and ``source`` are reserved for
    later features (brand pinning and external sourcing) and default to
    nullable/neutral values so no migration is needed when those land.
    """

    group: str | None = None
    name: str
    quantity: float | None = None
    unit: str | None = None
    note: str | None = None
    normalized_name: str | None = None
    brand_override: str | None = None
    source: str = "supermarket"

    def scaled(self, factor: float) -> "Ingredient":
        """Return a copy scaled by ``factor``.

        When ``quantity`` is ``None`` (e.g. "zout naar smaak") the quantity is
        left as ``None`` and only the copy is returned unchanged in that field.
        """
        new_quantity = None if self.quantity is None else self.quantity * factor
        return self.model_copy(update={"quantity": new_quantity})


class Step(BaseModel):
    """A single ordered cooking step with phase and duration range.

    ``instructions`` preserves the complete original text, including any
    reasoning, and is never summarized.
    """

    order: int
    title: str
    phase: Literal["prep", "cook", "finish"]
    duration_min_low: int | None = None
    duration_min_high: int | None = None
    instructions: str


class Recipe(BaseModel):
    """A complete recipe: metadata, grouped ingredients and ordered steps."""

    id: str
    title: str
    icon: str
    description: str
    servings: int
    category: Literal["meal", "bake"] = "meal"
    total_time_min_low: int | None = None
    total_time_min_high: int | None = None
    tags: list[str] = Field(default_factory=list)
    notes: str | None = None
    ingredients: list[Ingredient] = Field(default_factory=list)
    steps: list[Step] = Field(default_factory=list)
