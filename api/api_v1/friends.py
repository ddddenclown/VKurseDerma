from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_async_session
from core.security import get_current_user
from models.friendship import Friendship
from models.user import User
from crud.friendship import send_friend_request, update_friendship_status, get_friendship, get_user_friends
from schemas.friendship import FriendshipCreate, FriendshipOut, FriendshipStatusUpdate, UserWithFriends

router = APIRouter(tags=["friends"])

@router.post("/request", response_model=FriendshipOut, status_code=status.HTTP_201_CREATED)
async def senf_friend_request_endpoint(
        request: FriendshipCreate,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_async_session),
):
    if current_user.id == request.friend_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot send friend request to yourself!"
        )

    friendship = await send_friend_request(db, current_user.id, request.friend_id)
    if not friendship:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Friendship already exists or request already sent"
        )
    return friendship

@router.put("/{friendship_id}", response_model=FriendshipOut)
async def update_friendship_status_endpoint(
        friendship_id: int,
        status_update: FriendshipStatusUpdate,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_async_session)
):
    result = await db.execute(
        select(Friendship).filter(
            Friendship.id == friendship_id
        )
    )
    friendship = result.scalars().first()

    if not friendship or friendship.friend_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Friendship request not found"
        )

    if friendship.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Friendship request already processed"
        )

    updated_friendship = await update_friendship_status(db, friendship_id, status_update.status)


@router.get("/me", response_model=UserWithFriends)
async def get_my_friends(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_async_session),
):
    friends = await get_user_friends(db, current_user.id)

    stmt = (
        select(User)
        .join(
            Friendship,
            and_(
                Friendship.user_id == User.id,
                Friendship.friend_id == current_user.id,
                Friendship.status == "pending"
            )
        )
    )

    result = await db.execute(stmt)
    pending_requests = result.scalars().all()

    return UserWithFriends(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        friends=friends,
        pending_requests=pending_requests,
    )


@router.get("/status/{friend_id}", response_model=FriendshipOut)
async def get_friendship_status(
        friend_id: int,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_async_session),
):
    friendship = await get_friendship(db, current_user.id, friend_id)
    if not friendship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No friendship found"
        )
    return friendship