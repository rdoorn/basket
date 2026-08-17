"""Week-menu repository port.

Abstract interface for loading and persisting the single current
:class:`WeekMenu` document. The Motor adapter stores it under ``_id="current"``.
"""
from abc import ABC, abstractmethod

from app.domain.menu import WeekMenu


class MenuRepo(ABC):
    """Abstract repository for the current week menu."""

    @abstractmethod
    async def load(self) -> WeekMenu:
        """Return the stored menu, or an empty :class:`WeekMenu` when absent."""
        raise NotImplementedError

    @abstractmethod
    async def save(self, menu: WeekMenu) -> None:
        """Upsert ``menu`` as the single current document."""
        raise NotImplementedError
