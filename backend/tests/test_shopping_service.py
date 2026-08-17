"""Unit tests for the shopping-list aggregation/scaling service."""
from app.domain.recipe import Recipe, Ingredient
from app.domain.menu import WeekMenu, DayAssignment
from app.domain.shopping import ShoppingListItem
from app.services.shopping_service import (
    build_breakdown,
    build_shopping_list,
    partition_staples,
)


def _recipe():
    return Recipe(
        id="A", title="t", icon="🍝", description="", servings=4,
        total_time_min_low=50, total_time_min_high=60, tags=[], notes=None,
        ingredients=[
            Ingredient(name="macaroni", quantity=350, unit="g"),
            Ingredient(name="ui", quantity=1, unit="stuk"),
        ],
        steps=[],
    )


def test_scales_and_aggregates_same_ingredient():
    menu = WeekMenu()
    menu.set("d1", DayAssignment(recipe_id="A", multiplier=1.0))
    menu.set("d2", DayAssignment(recipe_id="A", multiplier=2.0))
    items = build_shopping_list(menu, {"A": _recipe()})
    by_name = {i.name: i for i in items}
    assert by_name["macaroni"].quantity == 1050  # 350 + 700
    assert by_name["ui"].quantity == 3


def test_none_quantity_listed_once_not_aggregated():
    recipe = Recipe(
        id="B", title="t", icon="🌿", description="", servings=4,
        total_time_min_low=None, total_time_min_high=None, tags=[], notes=None,
        ingredients=[Ingredient(name="zout", quantity=None, unit=None)],
        steps=[],
    )
    menu = WeekMenu()
    menu.set("d1", DayAssignment(recipe_id="B", multiplier=1.0))
    menu.set("d2", DayAssignment(recipe_id="B", multiplier=2.0))
    items = build_shopping_list(menu, {"B": recipe})
    zout = [i for i in items if i.name == "zout"]
    assert len(zout) == 1
    assert zout[0].quantity is None


def test_mixed_quantified_and_none_merge_to_one_line():
    # Same (name, unit) appearing once with a quantity and once as None must
    # collapse to a single line keeping the known quantity, not two rows.
    recipe = Recipe(
        id="M", title="t", icon="🧂", description="", servings=4,
        total_time_min_low=None, total_time_min_high=None, tags=[], notes=None,
        ingredients=[
            Ingredient(name="peper", quantity=2, unit=None),
            Ingredient(name="peper", quantity=None, unit=None),
        ],
        steps=[],
    )
    menu = WeekMenu()
    menu.set("d1", DayAssignment(recipe_id="M", multiplier=1.0))
    items = build_shopping_list(menu, {"M": recipe})
    peper = [i for i in items if i.name == "peper"]
    assert len(peper) == 1
    assert peper[0].quantity == 2


def test_different_units_are_not_merged():
    recipe = Recipe(
        id="C", title="t", icon="🧀", description="", servings=4,
        total_time_min_low=None, total_time_min_high=None, tags=[], notes=None,
        ingredients=[
            Ingredient(name="kaas", quantity=100, unit="g"),
            Ingredient(name="kaas", quantity=1, unit="stuk"),
        ],
        steps=[],
    )
    menu = WeekMenu()
    menu.set("d1", DayAssignment(recipe_id="C", multiplier=1.0))
    items = build_shopping_list(menu, {"C": recipe})
    kaas = sorted((i.unit, i.quantity) for i in items if i.name == "kaas")
    assert kaas == [("g", 100), ("stuk", 1)]


def test_aggregates_by_normalized_name():
    recipe = Recipe(
        id="D", title="t", icon="🍅", description="", servings=4,
        total_time_min_low=None, total_time_min_high=None, tags=[], notes=None,
        ingredients=[
            Ingredient(name="rode ui", normalized_name="ui", quantity=1, unit="stuk"),
            Ingredient(name="witte ui", normalized_name="ui", quantity=2, unit="stuk"),
        ],
        steps=[],
    )
    menu = WeekMenu()
    menu.set("d1", DayAssignment(recipe_id="D", multiplier=1.0))
    items = build_shopping_list(menu, {"D": recipe})
    ui = [i for i in items if i.quantity == 3]
    assert len(ui) == 1


def test_preserves_source_and_sorted_by_name():
    recipe = Recipe(
        id="E", title="t", icon="🥩", description="", servings=4,
        total_time_min_low=None, total_time_min_high=None, tags=[], notes=None,
        ingredients=[
            Ingredient(name="ui", quantity=1, unit="stuk"),
            Ingredient(name="gehakt", quantity=300, unit="g", source="external"),
        ],
        steps=[],
    )
    menu = WeekMenu()
    menu.set("d1", DayAssignment(recipe_id="E", multiplier=1.0))
    items = build_shopping_list(menu, {"E": recipe})
    assert [i.name for i in items] == ["gehakt", "ui"]
    assert {i.name: i.source for i in items}["gehakt"] == "external"


def test_missing_recipe_id_is_skipped():
    menu = WeekMenu()
    menu.set("d1", DayAssignment(recipe_id="ghost", multiplier=1.0))
    items = build_shopping_list(menu, {})
    assert items == []


def _shopping_items() -> list[ShoppingListItem]:
    return [
        ShoppingListItem(name="macaroni", quantity=350, unit="g"),
        ShoppingListItem(name="gehakt", quantity=300, unit="g"),
        ShoppingListItem(name="olijfolie", quantity=2, unit="el"),
        ShoppingListItem(name="citroensap", quantity=0.5, unit="citroen"),
    ]


def test_partition_staples_splits_pantry_and_flags_them():
    breakdown = partition_staples(_shopping_items(), promoted_staples=[])
    buy = {i.name for i in breakdown.items}
    pantry = {i.name for i in breakdown.pantry}
    assert buy == {"macaroni"}
    assert pantry == {"gehakt", "olijfolie", "citroensap"}
    assert all(i.staple for i in breakdown.pantry)


def test_partition_promotes_named_staple_into_items():
    breakdown = partition_staples(_shopping_items(), promoted_staples=["gehakt"])
    buy = {i.name for i in breakdown.items}
    pantry = {i.name for i in breakdown.pantry}
    assert "gehakt" in buy
    assert "gehakt" not in pantry
    promoted = next(i for i in breakdown.items if i.name == "gehakt")
    assert promoted.staple is True


def test_partition_matches_staples_case_insensitively():
    items = [ShoppingListItem(name="Zwarte Peper", quantity=None, unit=None)]
    breakdown = partition_staples(items, promoted_staples=[])
    assert [i.name for i in breakdown.pantry] == ["Zwarte Peper"]


def test_build_breakdown_uses_menu_promoted_staples():
    recipe = Recipe(
        id="S", title="t", icon="🍝", description="", servings=4,
        total_time_min_low=None, total_time_min_high=None, tags=[], notes=None,
        ingredients=[
            Ingredient(name="macaroni", quantity=350, unit="g"),
            Ingredient(name="gehakt", quantity=300, unit="g"),
        ],
        steps=[],
    )
    menu = WeekMenu()
    menu.set("d1", DayAssignment(recipe_id="S", multiplier=1.0))
    menu.set_staple_buy("gehakt", True)
    breakdown = build_breakdown(menu, {"S": recipe})
    assert {i.name for i in breakdown.items} == {"macaroni", "gehakt"}
    assert breakdown.pantry == []
