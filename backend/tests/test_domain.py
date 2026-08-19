"""Unit tests for the pure domain entities."""
from app.domain.recipe import Recipe, Ingredient, Step
from app.domain.menu import WeekMenu, DayAssignment, ExtraAssignment


def test_ingredient_scaled():
    ing = Ingredient(name="macaroni", quantity=350, unit="g")
    assert ing.scaled(2.0).quantity == 700
    assert ing.scaled(0.5).quantity == 175


def test_ingredient_scaled_none_quantity_stays_none():
    ing = Ingredient(name="laurierblad", quantity=None, unit=None)
    assert ing.scaled(2.0).quantity is None


def test_weekmenu_assign_and_get():
    m = WeekMenu()
    m.set("2026-08-17", DayAssignment(recipe_id="r1", multiplier=1.0))
    assert m.get("2026-08-17").recipe_id == "r1"


def test_ingredient_reserved_fields_defaults():
    ing = Ingredient(name="macaroni", quantity=350, unit="g")
    assert ing.normalized_name is None
    assert ing.brand_override is None
    assert ing.source == "supermarket"


def test_ingredient_scaled_preserves_other_fields():
    ing = Ingredient(
        group="Pasta", name="macaroni", quantity=350, unit="g",
        note="al dente", normalized_name="macaroni", source="external",
    )
    scaled = ing.scaled(2.0)
    assert scaled.group == "Pasta"
    assert scaled.note == "al dente"
    assert scaled.normalized_name == "macaroni"
    assert scaled.source == "external"
    # original untouched (immutability of the scale operation)
    assert ing.quantity == 350


def test_weekmenu_remove_and_missing_get_returns_none():
    m = WeekMenu()
    m.set("d1", DayAssignment(recipe_id="A"))
    m.remove("d1")
    assert m.get("d1") is None
    assert m.get("nope") is None


def test_extras_add_update_remove():
    m = WeekMenu()
    m.set_extra("bread", 1.0)
    assert m.extras == [ExtraAssignment(recipe_id="bread", multiplier=1.0)]
    m.set_extra("bread", 2.0)  # update in place, no duplicate
    assert len(m.extras) == 1 and m.extras[0].multiplier == 2.0
    m.remove_extra("bread")
    assert m.extras == []


def test_recipe_defaults_to_meal_category():
    r = Recipe(id="x", title="t", icon="🍝", description="", servings=2)
    assert r.category == "meal"


def test_recipe_accepts_bake_category():
    r = Recipe(
        id="x", title="t", icon="🍞", description="", servings=8,
        category="bake",
    )
    assert r.category == "bake"


def test_step_and_recipe_construct():
    step = Step(
        order=1, title="Bak gehakt", phase="cook",
        duration_min_low=8, duration_min_high=10, instructions="Bak bruin.",
    )
    recipe = Recipe(
        id="A", title="t", icon="🍝", description="", servings=4,
        total_time_min_low=50, total_time_min_high=60, tags=["pasta"],
        notes=None, ingredients=[Ingredient(name="ui", quantity=1, unit="stuk")],
        steps=[step],
    )
    assert recipe.steps[0].phase == "cook"
    assert recipe.servings == 4
