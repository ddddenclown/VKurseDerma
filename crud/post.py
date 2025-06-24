from sqlalchemy import Result, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Tuple, Optional

from sqlalchemy.orm import selectinload

from models.post import Post, Media


async def create_post(
        db: AsyncSession,
        post_data: dict,
        author_id: int,
        media_data: List[dict] = None,
) -> Post:
    post = Post(**post_data, author_id=author_id)
    db.add(post)
    await db.commit()
    await db.refresh(post)

    if media_data:
        for media_item in media_data:
            media = Media(**media_item, post_id=post.id)
            db.add(media)
        await db.commit()
        await db.refresh(post)
    return post


async def get_user_posts(
        db: AsyncSession,
        user_id: int,
) -> List[Post]:
    result = await db.execute(
        select(Post)
        .where(Post.author_id == user_id)
        .order_by(Post.created_at.desc())
    )
    return result.scalars().all()


async def get_post_by_id(
        db: AsyncSession,
        post_id: int,
) -> Post:
    result = await db.execute(
        select(Post)
        .options(selectinload(Post.media))
        .where(Post.id == post_id)
    )
    return result.scalars().first()


async def update_post(
        db: AsyncSession,
        post: Post,
        update_data: dict,
) -> Post:
    for field, value in update_data.items():
        setattr(post, field, value)

    await db.commit()
    await db.refresh(post)
    return post


async def delete_post(
        db: AsyncSession,
        post: Post,
) -> None:
    await db.delete(post)
    await db.commit()


async def get_all_posts(
        db: AsyncSession,
        offset: int = 0,
        limit: int = 100,
) -> list[Post]:
    result = await db.execute(
        select(Post).
        offset(offset).
        limit(limit)
    )
    return result.scalars().all()


async def search_post_by_content(
        db: AsyncSession,
        search_query: str,
        limit: int = 100,
        offset: int = 0,
) -> List[Post]:
    if not search_query.strip():
        return []

    search_terms = search_query.split()  # Разбиваем запрос на отдельные слова

    if not search_terms:
        return []

    conditions = []
    for term in search_terms:
        term_condition = or_(
            Post.title.ilike(f"%{term}%"),
            Post.content.ilike(f"%{term}%")
        )
        conditions.append(term_condition)

    query = select(Post)

    if conditions:
        query = query.where(and_(*conditions))

    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    return result.scalars().all()


def get_document_icon(extension: str) -> str:
    icons = {
        "pdf": "/static/icons/pdf-icon.png",
        "doc": "/static/icons/word-icon.png",
        "docx": "/static/icons/word-icon.png",
        "xls": "/static/icons/excel-icon.png",
        "xlsx": "/static/icons/excel-icon.png",
        "ppt": "/static/icons/powerpoint-icon.png",
        "pptx": "/static/icons/powerpoint-icon.png",
        "txt": "/static/icons/text-icon.png",
        "csv": "/static/icons/csv-icon.png",
    }
    return icons.get(extension, "/static/icons/file-icon.png")