"""Motor-based pet-food repository adapter.

Maps between the Pydantic :class:`PetFood` (which uses ``id``) and the Mongo
document (which uses ``_id``). Accepts an injected database so tests can pass a
``mongomock_motor`` database and the app can pass a real Motor one.
"""
import uuid
from typing import Any

from app.domain.pet import PetFood
from app.ports.pet_food_repo import PetFoodRepo

_COLLECTION = "pet_foods"


def _to_doc(food: PetFood) -> dict[str, Any]:
    """Serialize ``food`` to a Mongo document, mapping ``id`` to ``_id``."""
    doc = food.model_dump()
    doc["_id"] = doc.pop("id")
    return doc


def _from_doc(doc: dict[str, Any]) -> PetFood:
    """Deserialize a Mongo ``doc`` to a :class:`PetFood`, mapping ``_id``."""
    data = dict(doc)
    data["id"] = data.pop("_id")
    return PetFood.model_validate(data)


class MongoPetFoodRepo(PetFoodRepo):
    """Store pet foods in a MongoDB collection via Motor."""

    def __init__(self, db: Any) -> None:
        """Create a repository backed by ``db``'s ``pet_foods`` collection."""
        self._collection = db[_COLLECTION]

    async def list(self) -> list[PetFood]:
        """Return all stored pet foods."""
        cursor = self._collection.find({})
        return [_from_doc(doc) async for doc in cursor]

    async def create(self, food: PetFood) -> PetFood:
        """Persist ``food``, generating an id when absent, and return it."""
        if not food.id:
            food = food.model_copy(update={"id": uuid.uuid4().hex})
        await self._collection.insert_one(_to_doc(food))
        return food

    async def delete(self, food_id: str) -> bool:
        """Delete ``food_id``; return ``True`` if a document was removed."""
        result = await self._collection.delete_one({"_id": food_id})
        return result.deleted_count > 0

    async def count(self) -> int:
        """Return the number of stored pet foods."""
        return await self._collection.count_documents({})
