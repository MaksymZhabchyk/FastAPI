"""API routers for profile management."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import profile as profile_crud
from app.database import get_db
from app.schemas.profile import Profile, ProfileCreate, ProfileUpdate

router = APIRouter(prefix="/profiles", tags=["Profiles"])


@router.get("/", response_model=list[Profile])
async def get_profiles(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    return await profile_crud.get_all_profiles(db, skip=skip, limit=limit)


@router.post("/users/{user_id}", response_model=Profile, status_code=status.HTTP_201_CREATED)
async def create_profile_for_user(
    user_id: int,
    profile_data: ProfileCreate,
    db: AsyncSession = Depends(get_db),
):
    existing = await profile_crud.get_profile_by_user_id(db, user_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile for this user already exists",
        )
    return await profile_crud.create_profile(db, user_id, profile_data)


@router.get("/{profile_id}", response_model=Profile)
async def get_profile(
    profile_id: int,
    db: AsyncSession = Depends(get_db),
):
    profile = await profile_crud.get_profile_by_id(db, profile_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )
    return profile


@router.put("/{profile_id}", response_model=Profile)
async def update_profile(
    profile_id: int,
    profile_data: ProfileUpdate,
    db: AsyncSession = Depends(get_db),
):
    profile = await profile_crud.update_profile(db, profile_id, profile_data)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )
    return profile


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(
    profile_id: int,
    db: AsyncSession = Depends(get_db),
):
    success = await profile_crud.delete_profile(db, profile_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )
    return None