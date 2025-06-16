from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.profiles import Profile


async def get_profile_by_user_id(
        db: AsyncSession,
        user_id: int,
) -> Profile | None:
    result = await db.execute(select(Profile).filter(Profile.user_id == user_id))
    return result.scalars().first()


async def create_profile(
        db: AsyncSession,
        user_id: int,
        profile_data: dict,
) -> Profile:
    profile = Profile(
        user_id=user_id,
        **profile_data
    )
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return profile


async def update_profile(
        db: AsyncSession,
        profile: Profile,
        profile_data: dict,
) -> Profile:
    for key, value in profile_data.items():
        if value is not None:
            setattr(profile, key, value)

    profile.updated_at = func.now()

    await db.commit()
    await db.refresh(profile)
    return profile