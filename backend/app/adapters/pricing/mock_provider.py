"""Deterministic mock pricing adapter for v0.1.

Prices are derived from a stable hash of the store name and ingredient name so
results are fully reproducible: no randomness, no clock. The same inputs always
yield the same unit price, while different stores and ingredients diverge.
"""
import hashlib

from app.domain.pricing import PricedItem, StoreQuote
from app.domain.shopping import ShoppingListItem
from app.ports.pricing_provider import PricingProvider


# Units measured by weight/volume are priced per 100 of that unit; everything
# else (stuk, teen, el, tl, citroen, ...) is priced per single unit.
_PER_100_UNITS = frozenset({"g", "gram", "ml"})


def _unit_price(store: str, name: str) -> float:
    """Return a stable reference price in euros for ``name`` at ``store``.

    Uses SHA-256 over ``"<store>|<name>"`` so the value is deterministic across
    processes and Python's hash randomization. Prices land in the range
    0.40–3.39, rounded to cents — a plausible shelf/per-100g price so basket
    totals stay realistic for the mock.
    """
    digest = hashlib.sha256(f"{store}|{name}".encode("utf-8")).hexdigest()
    cents = int(digest[:8], 16) % 300  # 0..299
    return round(0.40 + cents / 100.0, 2)


def _line_factor(unit: str | None, quantity: float | None) -> float:
    """Return the multiplier applied to the unit price for a line.

    Unquantified lines (``quantity is None``) default to 1. Weight/volume units
    are billed per 100 (so 350 g costs 3.5x the per-100g price); all other units
    are billed per single unit.
    """
    if quantity is None:
        return 1.0
    if unit in _PER_100_UNITS:
        return quantity / 100.0
    return quantity


class MockPricingProvider(PricingProvider):
    """A deterministic fake store used until real adapters exist."""

    def __init__(self, store: str) -> None:
        """Create a provider for ``store``."""
        self.store = store

    def quote(self, items: list[ShoppingListItem]) -> StoreQuote:
        """Price every item and return the per-store quote with a total."""
        priced: list[PricedItem] = []
        for item in items:
            unit_price = _unit_price(self.store, item.name)
            factor = _line_factor(item.unit, item.quantity)
            line_total = round(unit_price * factor, 2)
            priced.append(
                PricedItem(
                    name=item.name,
                    quantity=item.quantity,
                    unit=item.unit,
                    unit_price=unit_price,
                    line_total=line_total,
                )
            )
        total = round(sum(p.line_total for p in priced), 2)
        return StoreQuote(store=self.store, items=priced, total=total)
