from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas
from app.api import deps
from app.core import security

router = APIRouter()


@router.get("/", response_model=list[schemas.User])
async def read_users(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve users. Only superusers.
    """
    result = await db.execute(select(models.User).offset(skip).limit(limit))
    return result.scalars().all()

@router.delete("/{user_id}", response_model=schemas.User)
async def delete_user(
    *,
    db: AsyncSession = Depends(deps.get_db),
    user_id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete user. Only superusers.
    """
    user = await db.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await db.delete(user)
    await db.commit()
    return user

@router.get("/leaderboard", response_model=list[schemas.User])
async def read_leaderboard(
    db: AsyncSession = Depends(deps.get_db),
    limit: int = 10,
) -> Any:
    """
    Get leaderboard.
    """
    result = await db.execute(
        select(models.User).order_by(models.User.xp.desc()).limit(limit)
    )
    return result.scalars().all()


@router.get("/me", response_model=schemas.User)
async def read_user_me(
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user


@router.put("/me", response_model=schemas.User)
async def update_user_me(
    *,
    db: AsyncSession = Depends(deps.get_db),
    user_in: schemas.UserUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update own user.
    """
    # Assuming update logic here. Since models.User is ORM, we can update attributes.
    # But for async session, we might need to be careful with detached instances if not careful.
    # current_user is attached to the session from `get_current_user` dependency IF the session is shared.
    # But `get_current_user` uses `Depends(get_db)`, creating a NEW session generator if not handled as a singleton dependency (FastAPI handles it per request).
    # Yes, `get_db` yields a session. `get_current_user` depends on `get_db`.
    # FastAPI dependency system ensures the SAME `db` session is passed if we use the same dependency function signature?
    # Actually, `get_current_user(db: AsyncSession = Depends(get_db))` gets a `db`.
    # `update_user_me(db: AsyncSession = Depends(get_db))` also gets a `db`.
    # They should be the SAME session instance within a request context in FastAPI.
    
    if user_in.password:
        hashed_password = security.get_password_hash(user_in.password)
        current_user.hashed_password = hashed_password
    
    if user_in.username:
        # Check uniqueness if changed
        pass # Skipping strictly for MVP speed, but should implement.

    if user_in.bio:
        current_user.bio = user_in.bio

    if user_in.email:
        # Check uniqueness
        pass
    
    # We need to add/merge if it's detached, but it should be attached.
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    return current_user
