"""FastAPI dependency providers.

Repositories are resolved through ``Depends`` so tests can override them via
``app.dependency_overrides`` with mongomock-backed implementations, while the
running app lazily creates a single real Motor client and database.
"""
from functools import lru_cache
from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient

from app.adapters.db.mongo_menu_repo import MongoMenuRepo
from app.adapters.db.mongo_pet_food_repo import MongoPetFoodRepo
from app.adapters.db.mongo_recipe_repo import MongoRecipeRepo
from app.adapters.pricing.mock_provider import MockPricingProvider
from app.config import get_settings
from app.ports.menu_repo import MenuRepo
from app.ports.pet_food_repo import PetFoodRepo
from app.ports.pricing_provider import PricingProvider
from app.ports.recipe_repo import RecipeRepo


@lru_cache(maxsize=1)
def get_database() -> Any:
    """Return the shared Motor database, created lazily on first use.

    Creating the client does not open a connection, so this is safe to call
    even when MongoDB is unavailable (e.g. at import time).
    """
    settings = get_settings()
    client = AsyncIOMotorClient(settings.mongo_url)
    return client[settings.mongo_db]


def get_recipe_repo() -> RecipeRepo:
    """Return the recipe repository bound to the shared database."""
    return MongoRecipeRepo(get_database())


def get_menu_repo() -> MenuRepo:
    """Return the menu repository bound to the shared database."""
    return MongoMenuRepo(get_database())


def get_pet_food_repo() -> PetFoodRepo:
    """Return the pet-food repository bound to the shared database."""
    return MongoPetFoodRepo(get_database())


def get_pricing_providers() -> list[PricingProvider]:
    """Return the pricing providers used by the Buy page (mock adapters)."""
    return [MockPricingProvider("Albert Heijn"), MockPricingProvider("Picnic")]
