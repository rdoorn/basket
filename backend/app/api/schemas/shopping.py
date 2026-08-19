"""Shopping-list request/response DTOs."""
from pydantic import BaseModel, Field

from app.domain.shopping import ShoppingBreakdown, ShoppingListItem


class ShoppingListOut(BaseModel):
    """Shopping list for ``GET /shopping-list``.

    ``items`` are the lines to order; ``pantry`` are the "heb ik vast wel"
    staples the user probably already has.
    """

    items: list[ShoppingListItem] = Field(default_factory=list)
    pantry: list[ShoppingListItem] = Field(default_factory=list)

    @classmethod
    def from_breakdown(cls, breakdown: ShoppingBreakdown) -> "ShoppingListOut":
        """Wrap a :class:`ShoppingBreakdown` into the response envelope."""
        return cls(items=breakdown.items, pantry=breakdown.pantry)


class ItemBuyIn(BaseModel):
    """Request body for moving an ingredient between the two lists.

    ``buy=True`` puts it on the shopping list; ``buy=False`` moves it to the
    "heb ik vast wel" list. Works for any ingredient, not just staples.
    """

    name: str
    buy: bool
