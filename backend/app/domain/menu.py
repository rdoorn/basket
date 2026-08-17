"""Week-menu domain entities: DayAssignment and WeekMenu.

The menu maps ISO date strings to a single assignment (one recipe per day in
v0.1). ``WeekMenu`` exposes small pure helpers; higher-level move/swap
resolution lives in ``app.services.menu_service``.
"""
from pydantic import BaseModel, Field

from app.domain.staples import normalize_staple


class DayAssignment(BaseModel):
    """A recipe assigned to a day with a portion multiplier."""

    recipe_id: str
    multiplier: float = 1.0


class WeekMenu(BaseModel):
    """A collection of per-date assignments keyed by ISO date string.

    ``promoted_staples`` holds the normalized names of staple ingredients the
    user has chosen to actually buy (moved from the "heb ik vast wel" list into
    the shopping list). It persists with the menu.
    """

    assignments: dict[str, DayAssignment] = Field(default_factory=dict)
    promoted_staples: list[str] = Field(default_factory=list)

    def get(self, date: str) -> DayAssignment | None:
        """Return the assignment for ``date`` or ``None`` when empty."""
        return self.assignments.get(date)

    def set(self, date: str, assignment: DayAssignment) -> None:
        """Assign ``assignment`` to ``date``, replacing any existing one."""
        self.assignments[date] = assignment

    def remove(self, date: str) -> None:
        """Clear ``date`` if present; a no-op when the day is already empty."""
        self.assignments.pop(date, None)

    def set_staple_buy(self, name: str, buy: bool) -> None:
        """Promote (``buy=True``) or un-promote a staple, keyed by name.

        Idempotent: promoting an already-promoted staple, or un-promoting one
        that is not promoted, is a no-op.
        """
        key = normalize_staple(name)
        if buy and key not in self.promoted_staples:
            self.promoted_staples.append(key)
        elif not buy and key in self.promoted_staples:
            self.promoted_staples.remove(key)
