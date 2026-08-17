"""Shopping-list response DTO."""
from pydantic import BaseModel, Field

from app.domain.shopping import ShoppingListItem


class ShoppingListOut(BaseModel):
    """Aggregated, scaled shopping list for ``GET /shopping-list``."""

    items: list[ShoppingListItem] = Field(default_factory=list)

    @classmethod
    def from_items(cls, items: list[ShoppingListItem]) -> "ShoppingListOut":
        """Wrap ``items`` into the response envelope."""
        return cls(items=items)
