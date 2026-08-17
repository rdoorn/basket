"""Week-menu domain entities: DayAssignment and WeekMenu.

The menu maps ISO date strings to a single assignment (one recipe per day in
v0.1). ``WeekMenu`` exposes small pure helpers; higher-level move/swap
resolution lives in ``app.services.menu_service``.
"""
from pydantic import BaseModel, Field


class DayAssignment(BaseModel):
    """A recipe assigned to a day with a portion multiplier."""

    recipe_id: str
    multiplier: float = 1.0


class WeekMenu(BaseModel):
    """A collection of per-date assignments keyed by ISO date string."""

    assignments: dict[str, DayAssignment] = Field(default_factory=dict)

    def get(self, date: str) -> DayAssignment | None:
        """Return the assignment for ``date`` or ``None`` when empty."""
        return self.assignments.get(date)

    def set(self, date: str, assignment: DayAssignment) -> None:
        """Assign ``assignment`` to ``date``, replacing any existing one."""
        self.assignments[date] = assignment

    def remove(self, date: str) -> None:
        """Clear ``date`` if present; a no-op when the day is already empty."""
        self.assignments.pop(date, None)
