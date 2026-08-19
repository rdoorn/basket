"""Staple request/response DTOs.

The "heb ik vast wel" list is exposed as ``{id, name}``. Names are normalized
(trimmed, lower-cased) by the repository on create, so ``StapleOut.name`` is
always the canonical form.
"""
from pydantic import BaseModel

from app.domain.staple import Staple


class StapleOut(BaseModel):
    """A single staple in responses."""

    id: str
    name: str

    @classmethod
    def from_staple(cls, staple: Staple) -> "StapleOut":
        """Build the DTO from a domain :class:`Staple`."""
        return cls(id=staple.id, name=staple.name)


class StapleIn(BaseModel):
    """Body for ``POST /staples`` (add a staple to the list)."""

    name: str
