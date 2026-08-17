"""Unit tests for the menu move/swap/assign service."""
from app.domain.menu import WeekMenu, DayAssignment
from app.services.menu_service import move_or_swap, assign


def _menu():
    m = WeekMenu()
    m.set("d1", DayAssignment(recipe_id="A", multiplier=1.0))
    return m


def test_move_to_empty_day():
    m = _menu()
    move_or_swap(m, src="d1", dst="d2")
    assert m.get("d2").recipe_id == "A"
    assert m.get("d1") is None


def test_swap_two_days():
    m = _menu()
    m.set("d2", DayAssignment(recipe_id="B", multiplier=2.0))
    move_or_swap(m, src="d1", dst="d2")
    assert m.get("d2").recipe_id == "A"
    assert m.get("d1").recipe_id == "B"
    assert m.get("d1").multiplier == 2.0


def test_move_from_empty_source_is_noop():
    m = WeekMenu()
    m.set("d2", DayAssignment(recipe_id="B"))
    move_or_swap(m, src="d1", dst="d2")
    assert m.get("d2").recipe_id == "B"
    assert m.get("d1") is None


def test_move_same_day_is_noop():
    m = _menu()
    move_or_swap(m, src="d1", dst="d1")
    assert m.get("d1").recipe_id == "A"


def test_assign_sets_new_assignment():
    m = WeekMenu()
    assign(m, date="d1", recipe_id="A", multiplier=2.0)
    assert m.get("d1").recipe_id == "A"
    assert m.get("d1").multiplier == 2.0


def test_assign_replaces_existing():
    m = _menu()
    assign(m, date="d1", recipe_id="B", multiplier=0.5)
    assert m.get("d1").recipe_id == "B"
    assert m.get("d1").multiplier == 0.5
