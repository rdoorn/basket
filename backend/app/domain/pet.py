"""Pet-food domain entities.

A :class:`PetFood` is one editable entry in the pet's food list. ``weight_g``
is a static guess of grams per purchase-unit (the store does not tell us up
front); the weight-driven generator in ``app.services.pet_service`` uses it only
as a guide to decide how many foods to select.
"""
from pydantic import BaseModel


class PetFood(BaseModel):
    """A single food the pet likes, with a guessed weight per purchase-unit."""

    id: str
    name: str
    weight_g: int
