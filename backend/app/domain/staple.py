"""Staple domain entity.

A :class:`Staple` is one editable entry in the "heb ik vast wel" list — an
ingredient the user usually has in stock. Its ``name`` is stored normalized
(trimmed, lower-cased) so shopping-list matching is case-insensitive.
"""
from pydantic import BaseModel


class Staple(BaseModel):
    """A single "heb ik vast wel" pantry staple."""

    id: str
    name: str
