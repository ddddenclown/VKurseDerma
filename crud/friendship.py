from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from models.friendship import Friendship
from models.user import User


async def send_friend_request(
        db: AsyncSession,
        user_id: int,
        friend_id: int,
) -> Friendship:
    existing = await db.execute(
        select(Friendship).filter(
            ((Friendship.user_id == user_id) & (Friendship.friend_id == friend_id)) |
            ((Friendship.user_id == friend_id) & (Friendship.friend_id == user_id))
        )
    )
    if existing.scalars().first():
        return None

    friendship = Friendship(
        user_id=user_id,
        friend_id=friend_id,
    )

    db.add(friendship)
    await db.commit()
    await db.refresh(friendship)
    return friendship


async def update_friendship_status(
        db: AsyncSession,
        friendship_id: int,
        status: str,
) -> Friendship:
    result = await db.execute(
        select(Friendship).filter(
            Friendship.id == friendship_id,
        )
    )

    friendship = result.scalars().first()
    if not friendship:
        return None

    friendship.status = status
    await db.commit()
    await db.refresh(friendship)
    return friendship


async def get_friendship(
        db: AsyncSession,
        user_id: int,
        friend_id: int
) -> Friendship:
    result = await db.execute(
        select(Friendship).filter(
            ((Friendship.user_id == user_id) & (Friendship.friend_id == friend_id)) |
            ((Friendship.user_id == friend_id) & (Friendship.friend_id == user_id))
        )
    )
    return result.scalars().first()


async def get_user_friends(
        db: AsyncSession,
        user_id: int,
) -> list[User]:
    result = await db.execute(
        select(User)
        .options(
            selectinload(User.friendships_initiated)
            .selectinload(Friendship.friend),
            selectinload(User.friendships_received)
            .selectinload(Friendship.user)
        )
        .where(User.id == user_id)
    )
    user = result.scalars().first()
    if not user:
        return []
    friends = []
    for f in user.friendships_initiated + user.friendships_received:
        if f.status == "accepted":
            friend = f.friend if f.user_id == user_id else f.user
            friends.append(friend)
    return friends
