"""Unit tests for staple detection and menu promotion state."""
from app.domain.menu import WeekMenu
from app.domain.staples import is_staple


def test_is_staple_known_and_case_insensitive():
    assert is_staple("gehakt")
    assert is_staple("Zwarte Peper")
    assert is_staple(" olijfolie ")


def test_is_staple_excludes_non_staples_and_citroenrasp():
    assert not is_staple("macaroni")
    assert not is_staple("citroenrasp")  # only citroensap is a staple


def test_set_staple_buy_promote_and_unpromote_idempotent():
    menu = WeekMenu()
    menu.set_staple_buy("Gehakt", True)
    assert menu.promoted_staples == ["gehakt"]
    menu.set_staple_buy("gehakt", True)  # idempotent
    assert menu.promoted_staples == ["gehakt"]
    menu.set_staple_buy("gehakt", False)
    assert menu.promoted_staples == []
    menu.set_staple_buy("gehakt", False)  # idempotent
    assert menu.promoted_staples == []
