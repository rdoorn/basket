"""FastAPI application entry point.

Wires CORS (for the frontend origin), the routers, and a guarded startup that
seeds the recipe library when the database is reachable and empty. The seed is
wrapped in a try/except so importing/starting the app never fails when MongoDB
is unavailable (e.g. under tests, which override the repositories anyway).
"""
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.deps import get_pet_food_repo, get_recipe_repo, get_staple_repo
from app.api.routers import (
    pet,
    pricing,
    recipes,
    shopping,
    staples,
    weekmenu,
)
from app.seed import (
    seed_missing,
    seed_pet_foods_missing,
    seed_staples_if_empty,
)

logger = logging.getLogger(__name__)

FRONTEND_ORIGIN = "http://localhost:8173"


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Seed the recipe library on startup when the database is reachable.

    Any failure (e.g. MongoDB not yet up) is logged and swallowed so the app
    still starts; the seed will happen on a later start once Mongo is ready.
    Tests override the repositories, so this is effectively a no-op there.
    """
    try:
        await seed_missing(get_recipe_repo())
        await seed_pet_foods_missing(get_pet_food_repo())
        await seed_staples_if_empty(get_staple_repo())
    except Exception as exc:  # noqa: BLE001 - startup must never crash on seed
        logger.warning("Startup seed skipped: %s", exc)
    yield


app = FastAPI(title="Basket API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(recipes.router)
app.include_router(weekmenu.router)
app.include_router(shopping.router)
app.include_router(pricing.router)
app.include_router(pet.router)
app.include_router(staples.router)
