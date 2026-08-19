"""Pet-food request/response DTOs.

Bodies and responses use camelCase (``weightG``, ``targetG``) to match the
frontend, while the domain keeps snake_case (``weight_g``, ``target_g``).
"""
from pydantic import BaseModel, ConfigDict

from app.domain.pet import PetFood


def _to_camel(name: str) -> str:
    """Convert ``snake_case`` to ``camelCase`` for alias generation."""
    head, *tail = name.split("_")
    return head + "".join(part.capitalize() for part in tail)


class PetFoodOut(BaseModel):
    """A single pet food in responses (camelCase)."""

    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)

    id: str
    name: str
    weight_g: int

    @classmethod
    def from_food(cls, food: PetFood) -> "PetFoodOut":
        """Build the DTO from a domain :class:`PetFood`."""
        return cls(id=food.id, name=food.name, weight_g=food.weight_g)


class PetFoodIn(BaseModel):
    """Body for ``POST /pet/foods`` (add a food to the list)."""

    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)

    name: str
    weight_g: int


class PetOut(BaseModel):
    """Current pet state for ``GET /pet`` and mutation responses.

    ``selection`` resolves each chosen food name back to its full record so the
    UI can show and re-roll it; unknown names are dropped. ``covered_g`` is the
    leftover coverage from recipe overlaps for the current menu.
    """

    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)

    target_g: int
    selection: list[PetFoodOut]
    covered_g: int = 0

    @classmethod
    def build(
        cls,
        target_g: int,
        selection: list[str],
        foods: list[PetFood],
        covered_g: int = 0,
    ) -> "PetOut":
        """Build the response, resolving ``selection`` names against ``foods``.

        :param covered_g: leftover coverage in grams from recipe overlaps.
        """
        by_name = {food.name: food for food in foods}
        resolved = [
            PetFoodOut.from_food(by_name[name])
            for name in selection
            if name in by_name
        ]
        return cls(target_g=target_g, selection=resolved, covered_g=covered_g)


class PetTargetIn(BaseModel):
    """Body for ``PUT /pet/target`` (set the weekly weight target in grams)."""

    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)

    target_g: int


class PetReplaceIn(BaseModel):
    """Body for ``POST /pet/replace`` (re-roll a single selected food)."""

    name: str
