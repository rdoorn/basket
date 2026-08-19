"""Pure, weight-driven pet-food selection service.

The service is deliberately free of Motor and FastAPI: it takes plain
``PetFood`` lists, an injected ``random.Random`` and a ``prices`` map
(``name -> price``) so it is fully deterministic under test. "Cheapest" is
resolved through that map, which the router builds by quoting the candidate
foods once via the pricing port — keeping pricing behind the port.

Selection is weight-driven, not count-driven. The guessed ``weight_g`` of each
food is only a guide to decide *how many* foods to pick; per-item grams are
never surfaced. Every selection starts with the single cheapest food as an
anchor, then adds random distinct foods until the summed guessed weight reaches
the target (capped at the list size so a short list can never loop forever).
"""
import random

from app.domain.pet import PetFood


def _by_name(foods: list[PetFood]) -> dict[str, PetFood]:
    """Return a ``name -> PetFood`` lookup."""
    return {food.name: food for food in foods}


def _total_weight(names: list[str], foods: list[PetFood]) -> int:
    """Return the summed guessed weight of ``names`` (unknown names count 0)."""
    lookup = _by_name(foods)
    return sum(lookup[n].weight_g for n in names if n in lookup)


def cheapest(foods: list[PetFood], prices: dict[str, float]) -> PetFood:
    """Return the cheapest food by ``prices`` (ties broken by name).

    Foods missing from ``prices`` are treated as infinitely expensive so a
    priced food always wins. Raises ``ValueError`` on an empty list.
    """
    if not foods:
        raise ValueError("cannot pick the cheapest of an empty food list")
    return min(
        foods,
        key=lambda food: (prices.get(food.name, float("inf")), food.name),
    )


def _fill(
    selection: list[str],
    foods: list[PetFood],
    target_g: int,
    rng: random.Random,
) -> list[str]:
    """Append random unselected foods to ``selection`` up to ``target_g``.

    Stops as soon as the summed guessed weight reaches ``target_g`` or every
    food is selected. Mutates and returns ``selection``.
    """
    remaining = [f.name for f in foods if f.name not in selection]
    rng.shuffle(remaining)
    for name in remaining:
        if _total_weight(selection, foods) >= target_g:
            break
        selection.append(name)
    return selection


def generate(
    foods: list[PetFood],
    prices: dict[str, float],
    target_g: int,
    rng: random.Random,
) -> list[str]:
    """Build a fresh selection: cheapest anchor, then random fill to weight.

    :param foods: the available pet foods.
    :param prices: ``name -> price`` map used only to pick the anchor.
    :param target_g: weekly weight target in grams (a guide, not a hard cap).
    :param rng: injected RNG so tests are deterministic.
    :returns: selected food names, anchor first; empty when ``foods`` is empty.
    """
    if not foods:
        return []
    selection = [cheapest(foods, prices).name]
    return _fill(selection, foods, target_g, rng)


def replace(
    selection: list[str],
    foods: list[PetFood],
    name: str,
    rng: random.Random,
) -> list[str]:
    """Swap ``name`` for a random food not currently selected (1:1).

    No-op (returns a copy of ``selection`` unchanged) when ``name`` is not
    selected or when every food is already selected. The total weight may drift
    slightly, which is acceptable since the weight is only a guide.
    """
    result = list(selection)
    if name not in result:
        return result
    candidates = [f.name for f in foods if f.name not in result]
    if not candidates:
        return result
    replacement = rng.choice(candidates)
    result[result.index(name)] = replacement
    return result


def adjust(
    selection: list[str],
    foods: list[PetFood],
    prices: dict[str, float],
    new_target_g: int,
    rng: random.Random,
) -> list[str]:
    """Re-approach ``new_target_g`` while keeping existing picks where possible.

    Grow: append random unselected foods until the target is reached. Shrink:
    drop trailing non-anchor picks while the total stays at or above the target,
    always keeping the cheapest anchor at the front. Regenerates from scratch
    when the current selection is empty.
    """
    if not foods:
        return []
    if not selection:
        return generate(foods, prices, new_target_g, rng)

    anchor = cheapest(foods, prices).name
    result = list(selection)
    # Ensure the anchor is present and leads the list so it is never dropped.
    if anchor in result:
        result.remove(anchor)
    result.insert(0, anchor)

    if _total_weight(result, foods) < new_target_g:
        return _fill(result, foods, new_target_g, rng)

    # Shrink: drop from the tail while staying at or above the target and never
    # removing the anchor (index 0).
    while len(result) > 1 and _total_weight(result[:-1], foods) >= new_target_g:
        result.pop()
    return result
