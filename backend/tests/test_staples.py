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


def test_set_item_buy_records_normalized_choice_idempotently():
    menu = WeekMenu()
    menu.set_item_buy("Gehakt", True)
    assert menu.item_choices == {"gehakt": True}
    menu.set_item_buy("gehakt", True)  # idempotent
    assert menu.item_choices == {"gehakt": True}
    menu.set_item_buy("gehakt", False)
    assert menu.item_choices == {"gehakt": False}


def test_set_item_buy_works_for_non_staples():
    menu = WeekMenu()
    menu.set_item_buy("rode paprika", False)
    assert menu.item_choices == {"rode paprika": False}
