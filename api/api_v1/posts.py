from fastapi import APIRouter, HTTPException, status, Depends, Query, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from core.database import get_async_session
from core.security import get_current_user
from core.file_upload import save_uploaded_file
from models.user import User
from schemas.post import PostCreate, PostUpdate, Post
from crud.post import (create_post, get_user_posts, get_post_by_id,
                       update_post, delete_post, get_all_posts,
                       search_post_by_content, get_document_icon)

router = APIRouter(tags=["posts"])


@router.post("/", response_model=Post, status_code=status.HTTP_201_CREATED)
async def create_new_post(
        title: str = Form(...),
        content: str = Form(...),
        media: List[UploadFile] = File([]),
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_async_session),
):
    media_data = []
    for file in media:
        media_info = await save_uploaded_file(file)
        media_data.append(media_info)

    post_dict = {
        "title": title,
        "content": content,
    }

    return await create_post(db, post_dict, current_user.id, media_data)


@router.get("/me", response_model=List[Post])
async def read_my_posts(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_async_session),
):
    return await get_user_posts(db, current_user.id)


@router.get("/all", response_model=List[Post])
async def read_all_posts(
        db: AsyncSession = Depends(get_async_session)
):
    return await get_all_posts(db)


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

    for media in post.media:
        if media.file_type == "document":
            extension = media.file_name.split('.')[-1].lower() if media.file_name else "file"
            media.icon = get_document_icon(extension)

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


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
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


@router.get("/search/", response_model=List[Post])
async def search_posts(
        q: str = Query(..., min_length=2, description="Поисковый запрос (минимум 2 символа)"),
        db: AsyncSession = Depends(get_async_session),
        limit: int = 20,
        offset: int = 0,
):
    try:
        result = await search_post_by_content(
            db,
            search_query=q,
            limit=limit,
            offset=offset,
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка поиска: {str(e)}"
        )