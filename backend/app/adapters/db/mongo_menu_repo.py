"""Motor-based week-menu repository adapter.

The whole menu is a single document under ``_id="current"``. ``load`` returns
an empty :class:`WeekMenu` when the document is absent; ``save`` upserts it.
"""
from typing import Any

from app.domain.menu import WeekMenu
from app.ports.menu_repo import MenuRepo

_COLLECTION = "weekmenu"
_DOC_ID = "current"


class MongoMenuRepo(MenuRepo):
    """Store the current week menu as a single MongoDB document."""

    def __init__(self, db: Any) -> None:
        """Create a repository backed by ``db``'s ``weekmenu`` collection."""
        self._collection = db[_COLLECTION]

    async def load(self) -> WeekMenu:
        """Return the stored menu, or an empty :class:`WeekMenu` when absent."""
        doc = await self._collection.find_one({"_id": _DOC_ID})
        if not doc:
            return WeekMenu()
        return WeekMenu.model_validate(
            {
                "assignments": doc.get("assignments", {}),
                "item_choices": doc.get("item_choices", {}),
                "extras": doc.get("extras", []),
                "pet_target_g": doc.get("pet_target_g", 1000),
                "pet_selection": doc.get("pet_selection", []),
            }
        )

    async def save(self, menu: WeekMenu) -> None:
        """Upsert ``menu`` as the single ``current`` document."""
        dump = menu.model_dump()
        payload: dict[str, Any] = {
            "assignments": dump["assignments"],
            "item_choices": dump["item_choices"],
            "extras": dump["extras"],
            "pet_target_g": dump["pet_target_g"],
            "pet_selection": dump["pet_selection"],
        }
        await self._collection.replace_one(
            {"_id": _DOC_ID},
            {"_id": _DOC_ID, **payload},
            upsert=True,
        )
