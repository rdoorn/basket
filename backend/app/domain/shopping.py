"""Shopping-list domain entity."""
from pydantic import BaseModel


class ShoppingListItem(BaseModel):
    """An aggregated, scaled shopping-list line.

    ``source`` carries the originating ingredient's sourcing (e.g.
    ``"supermarket"`` or ``"external"``) so downstream pricing can exclude
    non-store items from totals.
    """

    name: str
    quantity: float | None = None
    unit: str | None = None
    source: str = "supermarket"
