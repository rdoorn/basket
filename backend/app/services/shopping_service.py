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

    for assignment in menu.assignments.values():
        recipe = recipes_by_id.get(assignment.recipe_id)
        if recipe is None:
            continue
        for ingredient in recipe.ingredients:
            scaled = ingredient.scaled(assignment.multiplier)
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

    return sorted(aggregated.values(), key=lambda item: item.name)


def partition_items(
    items: list[ShoppingListItem],
    item_choices: dict[str, bool],
) -> ShoppingBreakdown:
    """Split ``items`` into a shopping list and a "heb ik vast wel" list.

    Each item's bucket is its explicit choice in ``item_choices`` when present,
    otherwise its default: staples default to the pantry, everything else to the
    shopping list. Items are flagged with their staple-ness for the UI.

    :param items: aggregated shopping-list lines.
    :param item_choices: normalized name -> buy? overrides.
    :returns: the split :class:`ShoppingBreakdown`.
    """
    to_buy: list[ShoppingListItem] = []
    pantry: list[ShoppingListItem] = []
    for item in items:
        staple = is_staple(item.name)
        buy = item_choices.get(normalize_name(item.name), not staple)
        flagged = item.model_copy(update={"staple": staple})
        (to_buy if buy else pantry).append(flagged)
    return ShoppingBreakdown(items=to_buy, pantry=pantry)


def build_breakdown(
    menu: WeekMenu,
    recipes_by_id: dict[str, Recipe],
) -> ShoppingBreakdown:
    """Build the aggregated shopping list split into to-buy and pantry lists."""
    items = build_shopping_list(menu, recipes_by_id)
    return partition_items(items, menu.item_choices)
