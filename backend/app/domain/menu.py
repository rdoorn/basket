"""Week-menu domain entities: DayAssignment and WeekMenu.

The menu maps ISO date strings to a single assignment (one recipe per day in
v0.1). ``WeekMenu`` exposes small pure helpers; higher-level move/swap
resolution lives in ``app.services.menu_service``.
"""
from pydantic import BaseModel, Field

from app.domain.staples import normalize_name


class DayAssignment(BaseModel):
    """A recipe assigned to a day with a portion multiplier."""

    recipe_id: str
    multiplier: float = 1.0


class ExtraAssignment(BaseModel):
    """A recipe added to the bag without a date (e.g. a bake).

    Carries the same portion multiplier as a day assignment so its
    ingredients scale identically in the shopping list.
    """

    recipe_id: str
    multiplier: float = 1.0


class WeekMenu(BaseModel):
    """A collection of per-date assignments keyed by ISO date string.

    ``item_choices`` maps a normalized ingredient name to an explicit bucket
    choice: ``True`` = put it on the shopping list, ``False`` = keep it in the
    "heb ik vast wel" list. Absent items fall back to their default (staples
    default to the pantry, everything else to the shopping list). Persists with
    the menu.

    ``extras`` holds dateless recipe assignments (bakes and the like) whose
    ingredients still belong in the shopping bag. ``pet_target_g`` and
    ``pet_selection`` carry the weekly pet-food generator state (weight target
    in grams and the currently chosen food names); both persist with the menu.
    """

    assignments: dict[str, DayAssignment] = Field(default_factory=dict)
    item_choices: dict[str, bool] = Field(default_factory=dict)
    extras: list[ExtraAssignment] = Field(default_factory=list)
    pet_target_g: int = 1000
    pet_selection: list[str] = Field(default_factory=list)

    def get(self, date: str) -> DayAssignment | None:
        """Return the assignment for ``date`` or ``None`` when empty."""
        return self.assignments.get(date)

    def set(self, date: str, assignment: DayAssignment) -> None:
        """Assign ``assignment`` to ``date``, replacing any existing one."""
        self.assignments[date] = assignment

    def remove(self, date: str) -> None:
        """Clear ``date`` if present; a no-op when the day is already empty."""
        self.assignments.pop(date, None)

    def set_item_buy(self, name: str, buy: bool) -> None:
        """Record whether ``name`` goes on the shopping list (``buy=True``) or
        the "heb ik vast wel" list (``buy=False``). Idempotent."""
        self.item_choices[normalize_name(name)] = buy

    def set_extra(self, recipe_id: str, multiplier: float = 1.0) -> None:
        """Add ``recipe_id`` as an extra, or update its multiplier in place.

        Upserts by ``recipe_id`` so a recipe never appears twice in the bag.
        """
        for extra in self.extras:
            if extra.recipe_id == recipe_id:
                extra.multiplier = multiplier
                return
        self.extras.append(
            ExtraAssignment(recipe_id=recipe_id, multiplier=multiplier)
        )

    def remove_extra(self, recipe_id: str) -> None:
        """Drop the extra for ``recipe_id`` if present; a no-op otherwise."""
        self.extras = [e for e in self.extras if e.recipe_id != recipe_id]
