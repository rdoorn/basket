"""Pricing provider port.

An abstract interface a store adapter must implement to quote a shopping
list. The v0.1 mock adapter and later real adapters (Albert Heijn, Picnic)
all slot in behind this same port.
"""
from abc import ABC, abstractmethod

from app.domain.pricing import StoreQuote
from app.domain.shopping import ShoppingListItem


class PricingProvider(ABC):
    """Abstract pricing provider for a single store."""

    store: str

    @abstractmethod
    def quote(self, items: list[ShoppingListItem]) -> StoreQuote:
        """Return a :class:`StoreQuote` pricing ``items`` for this store."""
        raise NotImplementedError
