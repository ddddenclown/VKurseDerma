from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List

from models.user import User
from schemas.user import UserCreate, UserWithDetails
from core.utils import hash_password

async def get_user_by_username(
        db: AsyncSession,
        username: str,
) -> User | None:
    result = await db.execute(
        select(User)
        .options(selectinload(User.profile))  # Добавьте эту строку
        .where(User.username == username)
    )
    return result.scalars().first()

async def get_user_by_email(
        db: AsyncSession,
        email: str
) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()


async def create_user(
        db: AsyncSession,
        user: UserCreate
) -> User:
    db_user = User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hash_password(user.password),
    )

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def get_all_users(
        db: AsyncSession,
        offset: int = 0,
        limit: int = 100,
) -> list[User]:
    result = await db.execute(
        select(
            User.id,
            User.username,
            User.email,
            User.full_name,
        )
        .offset(offset)
        .limit(limit)
    )
    return result.all()

async def search_user_by_username(
        db: AsyncSession,
        search_query: str,
        offset: int = 0,
        limit: int = 100,
) -> List[UserWithDetails]:
    result = await db.execute(
        select(User)
        .where(User.username.ilike(f"%{search_query}%"))
        .offset(offset)
        .limit(limit),
    )
    return result.scalars().all()