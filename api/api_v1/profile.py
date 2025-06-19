from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User
from models.profiles import Profile
from schemas.profile import ProfileCreate, ProfileUpdate, ProfileOut
from core.database import get_async_session
from core.security import get_current_user
from crud.profile import get_profile_by_user_id, create_profile, update_profile

router = APIRouter(tags=["profile"])


@router.post("/", response_model=ProfileOut, status_code=status.HTTP_201_CREATED)
async def create_profile_endpoint(
        profile_data: ProfileCreate,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_async_session),
):
    if current_user.profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profile already exists",
        )

    profile = await create_profile(
        db,
        current_user.id,
        profile_data.model_dump(exclude_unset=True)
    )
    return profile


@router.get("/", response_model=ProfileOut)
async def get_profile(
        current_user: User = Depends(get_current_user),
):
    if not current_user.profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    return current_user.profile


@router.put("/", response_model=ProfileOut)
async def update_profile_endpoint(
        profile_data: ProfileUpdate,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_async_session),

):
    if not current_user.profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

    profile = await update_profile(
        db,
        current_user.profile,
        profile_data.model_dump(exclude_unset=True)
    )
    return profile