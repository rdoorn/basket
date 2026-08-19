"""Staple ("heb ik vast wel") endpoints.

Thin router over the editable ``staples`` collection. The repository normalizes
each name on create, so the stored/returned name is always the canonical form
used by the shopping-list partition.
"""
from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_staple_repo
from app.api.schemas.staple import StapleIn, StapleOut
from app.domain.staple import Staple
from app.ports.staple_repo import StapleRepo

router = APIRouter(prefix="/staples", tags=["staples"])


@router.get("", response_model=list[StapleOut])
async def list_staples(
    repo: StapleRepo = Depends(get_staple_repo),
) -> list[StapleOut]:
    """Return the editable "heb ik vast wel" list."""
    staples = await repo.list()
    return [StapleOut.from_staple(staple) for staple in staples]


@router.post("", response_model=StapleOut)
async def add_staple(
    body: StapleIn, repo: StapleRepo = Depends(get_staple_repo)
) -> StapleOut:
    """Add a staple (id generated, name normalized) and return it."""
    created = await repo.create(Staple(id="", name=body.name))
    return StapleOut.from_staple(created)


@router.delete("/{staple_id}", response_model=list[StapleOut])
async def delete_staple(
    staple_id: str, repo: StapleRepo = Depends(get_staple_repo)
) -> list[StapleOut]:
    """Delete a staple; 404 when it does not exist. Returns the updated list."""
    if not await repo.delete(staple_id):
        raise HTTPException(status_code=404, detail="staple not found")
    remaining = await repo.list()
    return [StapleOut.from_staple(staple) for staple in remaining]
