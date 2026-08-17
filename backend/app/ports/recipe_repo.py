"""Recipe repository port.

Abstract interface for persisting and retrieving :class:`Recipe` entities.
The Motor-based adapter lives in ``app.adapters.db.mongo_recipe_repo``; tests
inject an in-memory mongomock-backed implementation of the same shape.
"""
from abc import ABC, abstractmethod

from app.domain.recipe import Recipe


class RecipeRepo(ABC):
    """Abstract repository for recipes."""

    @abstractmethod
    async def list(self) -> list[Recipe]:
        """Return all stored recipes."""
        raise NotImplementedError

    @abstractmethod
    async def get(self, recipe_id: str) -> Recipe | None:
        """Return the recipe with ``recipe_id`` or ``None`` when missing."""
        raise NotImplementedError

    @abstractmethod
    async def create(self, recipe: Recipe) -> Recipe:
        """Persist ``recipe`` (assigning an id when absent) and return it."""
        raise NotImplementedError

    @abstractmethod
    async def update(self, recipe_id: str, recipe: Recipe) -> Recipe | None:
        """Replace the recipe at ``recipe_id``; return it or ``None`` if absent."""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, recipe_id: str) -> bool:
        """Delete ``recipe_id``; return ``True`` if a document was removed."""
        raise NotImplementedError

    @abstractmethod
    async def count(self) -> int:
        """Return the number of stored recipes."""
        raise NotImplementedError
