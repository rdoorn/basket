"""Pricing domain entities: PricedItem and StoreQuote."""
from pydantic import BaseModel, Field


class PricedItem(BaseModel):
    """A single priced shopping-list line for one store."""

    name: str
    quantity: float | None = None
    unit: str | None = None
    unit_price: float
    line_total: float


class StoreQuote(BaseModel):
    """A per-store quote: the priced lines plus their total."""

    store: str
    items: list[PricedItem] = Field(default_factory=list)
    total: float = 0.0
