"""Pet-food repository port.

Abstract interface for the editable ``pet_foods`` collection. The Motor-based
adapter lives in ``app.adapters.db.mongo_pet_food_repo``; tests inject an
in-memory mongomock-backed implementation of the same shape.
"""
from abc import ABC, abstractmethod

from app.domain.pet import PetFood


class PetFoodRepo(ABC):
    """Abstract repository for the pet's food list."""

    @abstractmethod
    async def list(self) -> list[PetFood]:
        """Return all stored pet foods."""
        raise NotImplementedError

    @abstractmethod
    async def create(self, food: PetFood) -> PetFood:
        """Persist ``food`` (assigning an id when absent) and return it."""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, food_id: str) -> bool:
        """Delete ``food_id``; return ``True`` if a document was removed."""
        raise NotImplementedError

    @abstractmethod
    async def count(self) -> int:
        """Return the number of stored pet foods."""
        raise NotImplementedError
