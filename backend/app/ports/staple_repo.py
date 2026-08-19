"""Staple repository port.

Abstract interface for the editable ``staples`` collection. The Motor-based
adapter lives in ``app.adapters.db.mongo_staple_repo``; tests inject an
in-memory mongomock-backed implementation of the same shape.
"""
from abc import ABC, abstractmethod

from app.domain.staple import Staple


class StapleRepo(ABC):
    """Abstract repository for the "heb ik vast wel" staple list."""

    @abstractmethod
    async def list(self) -> list[Staple]:
        """Return all stored staples."""
        raise NotImplementedError

    @abstractmethod
    async def create(self, staple: Staple) -> Staple:
        """Persist ``staple`` (assigning an id when absent) and return it."""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, staple_id: str) -> bool:
        """Delete ``staple_id``; return ``True`` if a document was removed."""
        raise NotImplementedError

    @abstractmethod
    async def count(self) -> int:
        """Return the number of stored staples."""
        raise NotImplementedError
