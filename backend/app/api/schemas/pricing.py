"""Pricing response DTO."""
from pydantic import BaseModel, Field

from app.domain.pricing import StoreQuote


class PricingOut(BaseModel):
    """Per-store quotes for ``POST /pricing/quote``."""

    quotes: list[StoreQuote] = Field(default_factory=list)

    @classmethod
    def from_quotes(cls, quotes: list[StoreQuote]) -> "PricingOut":
        """Wrap ``quotes`` into the response envelope."""
        return cls(quotes=quotes)
