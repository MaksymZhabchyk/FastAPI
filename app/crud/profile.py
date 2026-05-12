"""CRUD operations for Profile."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import Profile
from app.schemas.profile import ProfileCreate, ProfileUpdate


async def create_profile(db: AsyncSession, user_id: int, profile: ProfileCreate) -> Profile:
    """Creates a profile for a user."""
    db_profile = Profile(user_id=user_id, **profile.model_dump())
    db.add(db_profile)
    await db.commit()
    await db.refresh(db_profile)
    return db_profile


async def get_profile_by_user_id(db: AsyncSession, user_id: int) -> Profile | None:
    """Gets a profile by user ID."""
    result = await db.execute(
        select(Profile).filter(Profile.user_id == user_id)
    )
    return result.scalars().first()


async def get_profile_by_id(db: AsyncSession, profile_id: int) -> Profile | None:
    """Gets a profile by ID."""
    result = await db.execute(
        select(Profile).filter(Profile.id == profile_id)
    )
    return result.scalars().first()


async def get_all_profiles(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Profile]:
    """Gets all profiles."""
    result = await db.execute(
        select(Profile).offset(skip).limit(limit)
    )
    return result.scalars().all()


async def update_profile(db: AsyncSession, profile_id: int, profile_update: ProfileUpdate) -> Profile | None:
    """Updates a profile."""
    db_profile = await get_profile_by_id(db, profile_id)
    if not db_profile:
        return None
    
    update_data = profile_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_profile, key, value)
    
    await db.commit()
    await db.refresh(db_profile)
    return db_profile


async def delete_profile(db: AsyncSession, profile_id: int) -> bool:
    """Deletes a profile."""
    db_profile = await get_profile_by_id(db, profile_id)
    if not db_profile:
        return False
    
    db.delete(db_profile)
    await db.commit()
    return True