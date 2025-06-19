from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from core.database import get_async_session
from crud.user import get_all_users, search_user_by_username
from schemas.user import UserWithDetails

router = APIRouter(
    prefix="/users",
    tags=["users"]
)


@router.get("/", response_model=List[UserWithDetails])
async def get_all_users_endpoint(
        offset: int = 0,
        limit: int = 0,
        db: AsyncSession = Depends(get_async_session),
):
    users = await get_all_users(db, offset=offset, limit=limit)
    return [
        UserWithDetails(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
        ) for user in users
    ]


@router.get("/search", response_model=List[UserWithDetails])
async def search_users_endpoint(
        query: str,
        offset: int = 0,
        limit: int = 100,
        db: AsyncSession = Depends(get_async_session),
):
    users = await search_user_by_username(db,
                                          search_query=query,
                                          offset=offset,
                                          limit=limit)
    return users
