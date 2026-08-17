"""Motor-based recipe repository adapter.

Maps between the Pydantic :class:`Recipe` (which uses ``id``) and the Mongo
document (which uses ``_id``). Accepts an injected database so tests can pass a
``mongomock_motor`` database and the app can pass a real Motor one.
"""
import uuid
from typing import Any

from app.domain.recipe import Recipe
from app.ports.recipe_repo import RecipeRepo

_COLLECTION = "recipes"


def _to_doc(recipe: Recipe) -> dict[str, Any]:
    """Serialize ``recipe`` to a Mongo document, mapping ``id`` to ``_id``."""
    doc = recipe.model_dump()
    doc["_id"] = doc.pop("id")
    return doc


def _from_doc(doc: dict[str, Any]) -> Recipe:
    """Deserialize a Mongo ``doc`` to a :class:`Recipe`, mapping ``_id``."""
    data = dict(doc)
    data["id"] = data.pop("_id")
    return Recipe.model_validate(data)


class MongoRecipeRepo(RecipeRepo):
    """Store recipes in a MongoDB collection via Motor."""

    def __init__(self, db: Any) -> None:
        """Create a repository backed by ``db``'s ``recipes`` collection."""
        self._collection = db[_COLLECTION]

    async def list(self) -> list[Recipe]:
        """Return all stored recipes."""
        cursor = self._collection.find({})
        return [_from_doc(doc) async for doc in cursor]

    async def get(self, recipe_id: str) -> Recipe | None:
        """Return the recipe with ``recipe_id`` or ``None`` when missing."""
        doc = await self._collection.find_one({"_id": recipe_id})
        return _from_doc(doc) if doc else None

    async def create(self, recipe: Recipe) -> Recipe:
        """Persist ``recipe``, generating an id when absent, and return it."""
        if not recipe.id:
            recipe = recipe.model_copy(update={"id": uuid.uuid4().hex})
        await self._collection.insert_one(_to_doc(recipe))
        return recipe

    async def update(self, recipe_id: str, recipe: Recipe) -> Recipe | None:
        """Replace the recipe at ``recipe_id``; return it or ``None`` if absent."""
        stored = recipe.model_copy(update={"id": recipe_id})
        result = await self._collection.replace_one(
            {"_id": recipe_id}, _to_doc(stored)
        )
        if result.matched_count == 0:
            return None
        return stored

    async def delete(self, recipe_id: str) -> bool:
        """Delete ``recipe_id``; return ``True`` if a document was removed."""
        result = await self._collection.delete_one({"_id": recipe_id})
        return result.deleted_count > 0

    async def count(self) -> int:
        """Return the number of stored recipes."""
        return await self._collection.count_documents({})
