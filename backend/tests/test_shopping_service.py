"""Unit tests for the shopping-list aggregation/scaling service."""
from app.domain.recipe import Recipe, Ingredient
from app.domain.menu import WeekMenu, DayAssignment
from app.services.shopping_service import build_shopping_list


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
