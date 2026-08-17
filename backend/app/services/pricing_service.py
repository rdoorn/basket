"""Pricing service: run a shopping list through pricing providers.

Callers pass the items that should actually be ordered (the to-buy list, which
already excludes un-promoted "heb ik vast wel" staples), so this service prices
exactly what it is given.
"""
from app.domain.pricing import StoreQuote
from app.domain.shopping import ShoppingListItem
from app.ports.pricing_provider import PricingProvider


def quote_all(
    items: list[ShoppingListItem],
    providers: list[PricingProvider],
) -> list[StoreQuote]:
    """Quote ``items`` against every provider.

    :param items: shopping-list items to order.
    :param providers: pricing providers to query.
    :returns: one :class:`StoreQuote` per provider.
    """
    return [provider.quote(items) for provider in providers]
