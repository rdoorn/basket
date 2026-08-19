"""Shopping service: derive a scaled, aggregated shopping list from a menu.

For each day assignment the referenced recipe's ingredients are scaled by the
assignment multiplier and aggregated by ``(normalized_name or name, unit)`` into
a single line per key. Merge policy when a key recurs:

* both quantities known  -> sum them;
* one quantity ``None``   -> keep the known quantity (a number beats "naar
  smaak");
* all quantities ``None`` -> keep ``None`` and list the item once.

The result is sorted by name.
"""
from app.domain.menu import WeekMenu
from app.domain.recipe import Recipe
from app.domain.shopping import ShoppingBreakdown, ShoppingListItem
from app.domain.staples import is_staple, normalize_name

PET_GROUP = "Huisdiervoer"


def build_shopping_list(
    menu: WeekMenu,
    recipes_by_id: dict[str, Recipe],
) -> list[ShoppingListItem]:
    """Build the aggregated, scaled shopping list for ``menu``.

    :param menu: the current week menu.
    :param recipes_by_id: lookup of recipes; assignments whose recipe is
        missing are skipped.
    :returns: shopping-list items sorted by name.
    """
    aggregated: dict[tuple[str, str | None], ShoppingListItem] = {}

    def add(recipe_id: str, multiplier: float) -> None:
        """Scale ``recipe_id``'s ingredients and merge them into ``aggregated``.

        A missing recipe is skipped. The merge policy matches day assignments:
        sum known quantities, prefer a number over ``None``, list ``None``
        items once.
        """
        recipe = recipes_by_id.get(recipe_id)
        if recipe is None:
            return
        for ingredient in recipe.ingredients:
            scaled = ingredient.scaled(multiplier)
            key = (scaled.normalized_name or scaled.name, scaled.unit)
            existing = aggregated.get(key)
            if existing is None:
                aggregated[key] = ShoppingListItem(
                    name=scaled.name,
                    quantity=scaled.quantity,
                    unit=scaled.unit,
                    source=scaled.source,
                )
                continue
            if scaled.quantity is None:
                continue
            if existing.quantity is None:
                existing.quantity = scaled.quantity
            else:
                existing.quantity += scaled.quantity

    for assignment in menu.assignments.values():
        add(assignment.recipe_id, assignment.multiplier)
    for extra in menu.extras:
        add(extra.recipe_id, extra.multiplier)

    return sorted(aggregated.values(), key=lambda item: item.name)


def partition_items(
    items: list[ShoppingListItem],
    item_choices: dict[str, bool],
    staples: set[str],
) -> ShoppingBreakdown:
    """Split ``items`` into a shopping list and a "heb ik vast wel" list.

    Each item's bucket is its explicit choice in ``item_choices`` when present,
    otherwise its default: staples default to the pantry, everything else to the
    shopping list. Items are flagged with their staple-ness for the UI.

    :param items: aggregated shopping-list lines.
    :param item_choices: normalized name -> buy? overrides.
    :param staples: normalized staple names (from the ``staples`` collection).
    :returns: the split :class:`ShoppingBreakdown`.
    """
    to_buy: list[ShoppingListItem] = []
    pantry: list[ShoppingListItem] = []
    for item in items:
        staple = is_staple(item.name, staples)
        buy = item_choices.get(normalize_name(item.name), not staple)
        flagged = item.model_copy(update={"staple": staple})
        (to_buy if buy else pantry).append(flagged)
    return ShoppingBreakdown(items=to_buy, pantry=pantry)


def pet_items(pet_selection: list[str]) -> list[ShoppingListItem]:
    """Turn the pet-food selection into buyable "Huisdiervoer" lines.

    One line per selected food, with no per-item grams (``quantity=None``), per
    the design: the weight is only an aggregate guide. Pet foods are never
    staples and never go to the pantry.
    """
    return [
        ShoppingListItem(name=name, quantity=None, unit=None, group=PET_GROUP)
        for name in pet_selection
    ]


def build_breakdown(
    menu: WeekMenu,
    recipes_by_id: dict[str, Recipe],
    staples: set[str],
) -> ShoppingBreakdown:
    """Build the aggregated shopping list split into to-buy and pantry lists.

    Recipe-derived items are aggregated and split by the pantry policy; the
    pet-food selection is appended to the buyable ``items`` under the
    "Huisdiervoer" group and never participates in the staple split.

    :param staples: normalized staple names (from the ``staples`` collection).
    """
    items = build_shopping_list(menu, recipes_by_id)
    breakdown = partition_items(items, menu.item_choices, staples)
    # Suppress a pet line whose normalized name is already a recipe item: the
    # recipe (Boodschappen) line wins so an overlap is never double-listed,
    # even when ``pet_selection`` is stale (design section 2, dedup).
    recipe_names = {normalize_name(item.name) for item in items}
    surviving = [
        name
        for name in menu.pet_selection
        if normalize_name(name) not in recipe_names
    ]
    breakdown.items.extend(pet_items(surviving))
    return breakdown
