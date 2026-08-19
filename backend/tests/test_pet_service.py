"""Tests for the pure, weight-driven pet-food selection service.

Randomness is injected via ``random.Random(0)`` and "cheapest" is fed through a
plain ``prices`` map, so every case is deterministic and the pricing port stays
behind the router (not exercised here).
"""
import random

from app.domain.pet import PetFood
from app.services import pet_service

# Distinct weights and prices so the cheapest anchor and fill order are stable.
FOODS = [
    PetFood(id="paprika", name="paprika", weight_g=150),
    PetFood(id="komkommer", name="komkommer", weight_g=400),
    PetFood(id="ijsbergsla", name="ijsbergsla", weight_g=400),
    PetFood(id="wortel", name="wortel", weight_g=80),
    PetFood(id="andijvie", name="andijvie", weight_g=300),
    PetFood(id="veldsla", name="veldsla", weight_g=100),
]
# wortel is the cheapest anchor.
PRICES = {
    "paprika": 1.20,
    "komkommer": 0.90,
    "ijsbergsla": 0.80,
    "wortel": 0.40,
    "andijvie": 0.70,
    "veldsla": 0.60,
}


def _weight(names: list[str]) -> int:
    by_name = {f.name: f for f in FOODS}
    return sum(by_name[n].weight_g for n in names)


def test_cheapest_picks_lowest_price():
    assert pet_service.cheapest(FOODS, PRICES).name == "wortel"


def test_generate_starts_with_cheapest_then_fills_to_target():
    selection = pet_service.generate(FOODS, PRICES, 1000, random.Random(0))
    assert selection[0] == "wortel"  # cheapest anchor first
    assert len(selection) == len(set(selection))  # no duplicates
    assert _weight(selection) >= 1000
    # Adding any earlier pick would already have crossed the target, so the
    # penultimate running total must be below it.
    assert _weight(selection[:-1]) < 1000


def test_generate_caps_at_list_size():
    # Target unreachable even with every food; must stop at the full list.
    selection = pet_service.generate(FOODS, PRICES, 100000, random.Random(0))
    assert len(selection) == len(FOODS)
    assert set(selection) == {f.name for f in FOODS}


def test_replace_swaps_for_unselected():
    selection = ["wortel", "veldsla"]
    result = pet_service.replace(selection, FOODS, "veldsla", random.Random(0))
    assert "veldsla" not in result
    assert "wortel" in result  # untouched pick stays
    assert len(result) == 2
    assert result[1] not in ("wortel", "veldsla")  # a genuinely new pick


def test_replace_noop_when_all_selected():
    selection = [f.name for f in FOODS]
    result = pet_service.replace(selection, FOODS, "wortel", random.Random(0))
    assert result == selection


def test_replace_noop_when_name_not_selected():
    selection = ["wortel"]
    result = pet_service.replace(selection, FOODS, "paprika", random.Random(0))
    assert result == selection


def test_adjust_target_grows():
    selection = ["wortel"]  # 80 g
    result = pet_service.adjust(selection, FOODS, PRICES, 1000, random.Random(0))
    assert result[0] == "wortel"  # existing pick kept
    assert _weight(result) >= 1000
    assert len(result) == len(set(result))


def test_adjust_target_shrinks_keeps_anchor():
    # Full list, ~1430 g; shrink to 300 g should drop trailing picks but keep
    # the cheapest anchor (wortel) at the front.
    selection = pet_service.generate(FOODS, PRICES, 100000, random.Random(0))
    result = pet_service.adjust(selection, FOODS, PRICES, 300, random.Random(0))
    assert result[0] == "wortel"  # cheapest anchor preserved
    assert len(result) < len(selection)
    assert _weight(result) >= 300


def test_adjust_shrink_to_zero_keeps_anchor():
    selection = pet_service.generate(FOODS, PRICES, 100000, random.Random(0))
    result = pet_service.adjust(selection, FOODS, PRICES, 0, random.Random(0))
    assert result == ["wortel"]  # anchor always survives


def test_coverage_g_is_half_standard_weight_of_overlaps():
    foods = [
        PetFood(id="i", name="ijsbergsla", weight_g=400),
        PetFood(id="p", name="paprika", weight_g=150),
    ]
    assert pet_service.coverage_g(foods, {"ijsbergsla"}) == 200
    # Multiple overlaps sum; rounding applies per food.
    assert pet_service.coverage_g(foods, {"ijsbergsla", "paprika"}) == 275
    # No overlap -> zero.
    assert pet_service.coverage_g(foods, set()) == 0


def test_generate_excludes_overlap_and_fills_effective_target():
    # target 1000, ijsbergsla overlaps -> covered 200 -> effective 800; the
    # pool excludes ijsbergsla so it never appears in the selection.
    selection = pet_service.generate(
        FOODS, PRICES, 1000, random.Random(0), exclude_names={"ijsbergsla"}
    )
    assert "ijsbergsla" not in selection
    assert selection[0] == "wortel"  # cheapest of the pool anchors
    assert _weight(selection) >= 800  # reaches the effective target
    # Penultimate total is below the effective target (fill stops as soon as
    # it is reached).
    assert _weight(selection[:-1]) < 800


def test_generate_empty_pool_returns_empty():
    foods = [PetFood(id="i", name="ijsbergsla", weight_g=400)]
    selection = pet_service.generate(
        foods, {"ijsbergsla": 0.8}, 1000, random.Random(0),
        exclude_names={"ijsbergsla"},
    )
    assert selection == []


def test_adjust_respects_exclude_and_coverage():
    # Selection already holds an excluded food; adjust must drop it and reach
    # only the effective target using the pool.
    selection = ["ijsbergsla", "wortel"]
    result = pet_service.adjust(
        selection, FOODS, PRICES, 1000, random.Random(0),
        exclude_names={"ijsbergsla"},
    )
    assert "ijsbergsla" not in result
    assert result[0] == "wortel"  # cheapest of the pool kept as anchor
    assert _weight(result) >= 800  # effective target (1000 - 200 covered)


def test_adjust_shrinks_to_effective_target_with_exclude():
    # A full-pool selection shrunk toward a small target still excludes the
    # overlap and keeps the anchor.
    selection = pet_service.generate(
        FOODS, PRICES, 100000, random.Random(0), exclude_names={"ijsbergsla"}
    )
    result = pet_service.adjust(
        selection, FOODS, PRICES, 300, random.Random(0),
        exclude_names={"ijsbergsla"},
    )
    assert "ijsbergsla" not in result
    assert result[0] == "wortel"
    assert _weight(result) >= 100  # effective target (300 - 200 covered)
