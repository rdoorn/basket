"""Staple ("heb ik vast wel") ingredient matching.

Staples are things you usually have in stock. They are split out of the shopping
list into a separate pantry list on the calendar; the user promotes one into the
shopping list with a single click when they actually need to buy it. Matched
case-insensitively by ingredient name against an injected staple set (the
editable ``staples`` collection loaded from the repository).
"""


def normalize_name(name: str) -> str:
    """Return the canonical (trimmed, lower-cased) form used for matching."""
    return name.strip().lower()


def is_staple(name: str, staples: set[str]) -> bool:
    """Return whether ``name`` is a staple in the given ``staples`` set.

    ``staples`` holds already-normalized names (as stored by the repo). Matching
    normalizes ``name`` the same way, so it is case-insensitive. Staple-ness only
    sets an ingredient's *default* bucket (staples default to the pantry list);
    the user can override any item's placement.
    """
    return normalize_name(name) in staples
