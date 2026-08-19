"""Motor-based staple repository adapter.

Maps between the Pydantic :class:`Staple` (which uses ``id``) and the Mongo
document (which uses ``_id``). Names are stored via ``normalize_name`` so the
shopping-list partition matches ingredients case-insensitively. Accepts an
injected database so tests can pass a ``mongomock_motor`` database and the app
can pass a real Motor one.
"""
import uuid
from typing import Any

from app.domain.staple import Staple
from app.domain.staples import normalize_name
from app.ports.staple_repo import StapleRepo

_COLLECTION = "staples"


def _to_doc(staple: Staple) -> dict[str, Any]:
    """Serialize ``staple`` to a Mongo document, mapping ``id`` to ``_id``."""
    doc = staple.model_dump()
    doc["_id"] = doc.pop("id")
    return doc


def _from_doc(doc: dict[str, Any]) -> Staple:
    """Deserialize a Mongo ``doc`` to a :class:`Staple`, mapping ``_id``."""
    data = dict(doc)
    data["id"] = data.pop("_id")
    return Staple.model_validate(data)


class MongoStapleRepo(StapleRepo):
    """Store staples in a MongoDB collection via Motor."""

    def __init__(self, db: Any) -> None:
        """Create a repository backed by ``db``'s ``staples`` collection."""
        self._collection = db[_COLLECTION]

    async def list(self) -> list[Staple]:
        """Return all stored staples."""
        cursor = self._collection.find({})
        return [_from_doc(doc) async for doc in cursor]

    async def create(self, staple: Staple) -> Staple:
        """Persist ``staple`` (id generated, name normalized) and return it."""
        staple = staple.model_copy(
            update={
                "id": staple.id or uuid.uuid4().hex,
                "name": normalize_name(staple.name),
            }
        )
        await self._collection.insert_one(_to_doc(staple))
        return staple

    async def delete(self, staple_id: str) -> bool:
        """Delete ``staple_id``; return ``True`` if a document was removed."""
        result = await self._collection.delete_one({"_id": staple_id})
        return result.deleted_count > 0

    async def count(self) -> int:
        """Return the number of stored staples."""
        return await self._collection.count_documents({})
