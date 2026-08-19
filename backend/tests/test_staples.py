"""Unit tests for staple detection and menu promotion state."""
from app.domain.menu import WeekMenu
from app.domain.staples import is_staple

# A representative staple set (the legacy defaults plus a bake staple), as the
# repo would supply it — names already normalized.
STAPLES = {
    "olijfolie",
    "citroensap",
    "chilivlokken",
    "gehakt",
    "rundergehakt",
    "zout",
    "zwarte peper",
    "venkelzaad",
    "suiker",
}


def test_is_staple_known_and_case_insensitive():
    assert is_staple("gehakt", STAPLES)
    assert is_staple("Zwarte Peper", STAPLES)
    assert is_staple(" olijfolie ", STAPLES)
    assert is_staple("Suiker", {"suiker"})


def test_is_staple_excludes_non_staples_and_citroenrasp():
    assert not is_staple("macaroni", STAPLES)
    assert not is_staple("citroenrasp", STAPLES)  # only citroensap is a staple
    assert not is_staple("macaroni", {"suiker"})


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
