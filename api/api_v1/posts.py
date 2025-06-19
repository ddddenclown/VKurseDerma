from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from core.database import get_async_session
from core.security import get_current_user
from models.user import User
from models.post import Post
from schemas.post import PostCreate, PostUpdate, Post
from crud.post import create_post, get_user_posts, get_post_by_id, update_post, delete_post

router = APIRouter(tags=["posts"])


@router.post("/", response_model=Post, status_code=status.HTTP_201_CREATED)
async def create_new_post(
        post_data: PostCreate,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_async_session),
):
    return await create_post(db, post_data.model_dump(), current_user.id)


@router.get("/me", response_model=List[Post])
async def read_my_posts(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_async_session),
):
    return await get_user_posts(db, current_user.id)


@router.get("/{post_id}", response_model=Post)
async def read_post_by_id(
        post_id: int,
        db: AsyncSession = Depends(get_async_session),
) -> Post:
    post = await get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )
    return post


@router.put("/{post_id}", response_model=Post)
async def update_existing_post(
        post_id: int,
        post_data: PostUpdate,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_async_session),
):
    post = await get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    if post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not your post"
        )

    return await update_post(db, post, post_data.model_dump(exclude_unset=True))


@router.delete("/{post_ud}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_post(
        post_id: int,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_async_session),
):
    post = await get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    if post.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not your post"
        )

    await delete_post(db, post)
    return None
