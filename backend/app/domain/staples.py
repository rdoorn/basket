"""Staple ("heb ik vast wel") ingredients.

Staples are things you usually have in stock. They are split out of the shopping
list into a separate pantry list on the calendar; the user promotes one into the
shopping list with a single click when they actually need to buy it. Matched
case-insensitively by ingredient name.
"""

STAPLE_INGREDIENTS: frozenset[str] = frozenset(
    {
        "olijfolie",
        "citroensap",
        "chilivlokken",
        "gehakt",
        "zout",
        "zwarte peper",
        "venkelzaad",
    }
)


def normalize_staple(name: str) -> str:
    """Return the canonical (trimmed, lower-cased) form used for matching."""
    return name.strip().lower()


def is_staple(name: str) -> bool:
    """Return whether ``name`` is a staple ("heb ik vast wel") ingredient."""
    return normalize_staple(name) in STAPLE_INGREDIENTS
