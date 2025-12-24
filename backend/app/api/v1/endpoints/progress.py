from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas
from app.api import deps

router = APIRouter()

@router.get("/", response_model=List[schemas.UserProgress])
async def read_user_progress(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve current user's progress.
    """
    result = await db.execute(
        select(models.UserProgress)
        .where(models.UserProgress.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

@router.post("/", response_model=schemas.UserProgress)
async def create_progress(
    *,
    db: AsyncSession = Depends(deps.get_db),
    progress_in: schemas.UserProgressCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create/Start progress for a route.
    """
    # Check if already exists
    result = await db.execute(
        select(models.UserProgress)
        .where(models.UserProgress.user_id == current_user.id)
        .where(models.UserProgress.route_id == progress_in.route_id)
    )
    existing = result.scalars().first()
    if existing:
        raise HTTPException(status_code=400, detail="Progress for this route already exists")

    progress = models.UserProgress(
        user_id=current_user.id,
        route_id=progress_in.route_id,
        status=progress_in.status,
        completed_points_count=progress_in.completed_points_count
    )
    db.add(progress)
    await db.commit()
    await db.refresh(progress)
    return progress

@router.put("/{progress_id}", response_model=schemas.UserProgress)
async def update_progress(
    *,
    db: AsyncSession = Depends(deps.get_db),
    progress_id: int,
    progress_in: schemas.UserProgressUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update progress (e.g. status, count).
    """
    progress = await db.get(models.UserProgress, progress_id)
    if not progress:
        raise HTTPException(status_code=404, detail="Progress not found")
    if progress.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    if progress_in.status is not None:
        progress.status = progress_in.status
    if progress_in.completed_points_count is not None:
        progress.completed_points_count = progress_in.completed_points_count
    
    db.add(progress)
    await db.commit()
    await db.refresh(progress)
    return progress
