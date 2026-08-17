"""Week-menu endpoints.

Routers delegate move/swap and assign resolution to ``menu_service`` and
persist the whole menu via the repository. The 14-day window is computed from
``date.today()``.
"""
from datetime import date, timedelta

from fastapi import APIRouter, Depends

from app.api.deps import get_menu_repo
from app.api.schemas.menu import (
    AssignmentInput,
    AssignmentOut,
    DayOut,
    WeekMenuOut,
    WindowOut,
)
from app.ports.menu_repo import MenuRepo
from app.services import menu_service

router = APIRouter(prefix="/weekmenu", tags=["weekmenu"])

_WINDOW_DAYS = 14


@router.get("", response_model=WindowOut)
async def get_weekmenu(repo: MenuRepo = Depends(get_menu_repo)) -> WindowOut:
    """Return today plus the next 13 days, each with its assignment or null."""
    menu = await repo.load()
    today = date.today()
    days: list[DayOut] = []
    for offset in range(_WINDOW_DAYS):
        day = (today + timedelta(days=offset)).isoformat()
        assignment = menu.get(day)
        days.append(
            DayOut(
                date=day,
                assignment=(
                    AssignmentOut.from_assignment(assignment)
                    if assignment is not None
                    else None
                ),
            )
        )
    return WindowOut(days=days)


@router.put("/assignments", response_model=WeekMenuOut)
async def put_assignment(
    body: AssignmentInput, repo: MenuRepo = Depends(get_menu_repo)
) -> WeekMenuOut:
    """Assign a recipe to a day, or move/swap when ``fromDate`` is given."""
    menu = await repo.load()
    if body.from_date is not None:
        menu_service.move_or_swap(menu, src=body.from_date, dst=body.date)
    else:
        menu_service.assign(
            menu,
            date=body.date,
            recipe_id=body.recipe_id,
            multiplier=body.multiplier,
        )
    await repo.save(menu)
    return WeekMenuOut.from_menu(menu)


@router.delete("/assignments/{day}", response_model=WeekMenuOut)
async def delete_assignment(
    day: str, repo: MenuRepo = Depends(get_menu_repo)
) -> WeekMenuOut:
    """Clear the assignment on ``day`` and persist the menu."""
    menu = await repo.load()
    menu.remove(day)
    await repo.save(menu)
    return WeekMenuOut.from_menu(menu)
