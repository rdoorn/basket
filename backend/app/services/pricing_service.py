"""Pricing service: run a shopping list through pricing providers.

External-source ingredients (e.g. farm ``gehakt``) are excluded from store
totals; only ``source == "supermarket"`` items are quoted.
"""
from app.domain.pricing import StoreQuote
from app.domain.shopping import ShoppingListItem
from app.ports.pricing_provider import PricingProvider


def quote_all(
    items: list[ShoppingListItem],
    providers: list[PricingProvider],
) -> list[StoreQuote]:
    """Quote ``items`` against every provider.

    :param items: shopping-list items; non-supermarket items are excluded.
    :param providers: pricing providers to query.
    :returns: one :class:`StoreQuote` per provider.
    """
    priceable = [item for item in items if item.source == "supermarket"]
    return [provider.quote(priceable) for provider in providers]
