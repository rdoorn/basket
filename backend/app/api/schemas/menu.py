"""Week-menu request/response DTOs.

Request bodies use camelCase (``recipeId``, ``fromDate``) to match the
frontend; responses expose the resolved menu and the 14-day window.
"""
from pydantic import BaseModel, ConfigDict, Field

from app.domain.menu import DayAssignment, WeekMenu


def _to_camel(name: str) -> str:
    """Convert ``snake_case`` to ``camelCase`` for alias generation."""
    head, *tail = name.split("_")
    return head + "".join(part.capitalize() for part in tail)


class AssignmentInput(BaseModel):
    """Body for ``PUT /weekmenu/assignments``.

    When ``from_date`` (``fromDate``) is present the request is a move/swap of
    an existing assignment; otherwise it assigns the recipe to ``date``.
    """

    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)

    date: str
    recipe_id: str
    multiplier: float = 1.0
    from_date: str | None = None


class AssignmentOut(BaseModel):
    """A single resolved assignment in menu responses (camelCase)."""

    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)

    recipe_id: str
    multiplier: float

    @classmethod
    def from_assignment(cls, assignment: DayAssignment) -> "AssignmentOut":
        """Build the DTO from a domain :class:`DayAssignment`."""
        return cls(
            recipe_id=assignment.recipe_id,
            multiplier=assignment.multiplier,
        )


class WeekMenuOut(BaseModel):
    """The full current menu keyed by ISO date string."""

    model_config = ConfigDict(populate_by_name=True)

    assignments: dict[str, AssignmentOut] = Field(default_factory=dict)

    @classmethod
    def from_menu(cls, menu: WeekMenu) -> "WeekMenuOut":
        """Build the response from a domain :class:`WeekMenu`."""
        return cls(
            assignments={
                day: AssignmentOut.from_assignment(assignment)
                for day, assignment in menu.assignments.items()
            }
        )


class DayOut(BaseModel):
    """One day of the 14-day window: its date and optional assignment."""

    date: str
    assignment: AssignmentOut | None = None


class WindowOut(BaseModel):
    """The 14-day window response for ``GET /weekmenu``."""

    days: list[DayOut] = Field(default_factory=list)
