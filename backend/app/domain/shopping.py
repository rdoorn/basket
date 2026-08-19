"""Shopping-list domain entities."""
from pydantic import BaseModel, Field


class ShoppingListItem(BaseModel):
    """An aggregated, scaled shopping-list line.

    ``source`` carries the originating ingredient's sourcing (reserved for later
    features). ``staple`` marks a "heb ik vast wel" ingredient so the UI can
    show a promote/un-promote control. ``group`` optionally sections the line in
    the UI (e.g. ``"Huisdiervoer"`` for pet foods); recipe-derived items leave
    it ``None``.
    """

    name: str
    quantity: float | None = None
    unit: str | None = None
    source: str = "supermarket"
    staple: bool = False
    group: str | None = None


class ShoppingBreakdown(BaseModel):
    """A shopping list split into items to buy and staples on hand.

    ``items`` are the lines to order (non-staples plus promoted staples);
    ``pantry`` are staple lines the user probably already has ("heb ik vast
    wel") and has not promoted.
    """

    items: list[ShoppingListItem] = Field(default_factory=list)
    pantry: list[ShoppingListItem] = Field(default_factory=list)
