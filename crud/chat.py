from sqlalchemy import select, and_, func, exists, update
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from typing import List

from models.chat import Conversation, Participant, Message
from models.user import User


async def create_conversation(
    db: AsyncSession,
    user_ids: List[int],
):
    unique_user_ids = list(set(user_ids))

    if len(unique_user_ids) != 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chat must have 2 users"
        )

    conv = Conversation()
    db.add(conv)
    await db.flush()

    for user_id in unique_user_ids:
        participant = Participant(user_id=user_id, conversation_id=conv.id)
        db.add(participant)

    await db.commit()

    return {
        "id": conv.id,
        "participants": unique_user_ids,
        "created_at": conv.created_at,
    }


async def get_user_conversations(db: AsyncSession, user_id: int):
    subq = (
        select(Participant.conversation_id)
        .where(Participant.user_id == user_id)
        .scalar_subquery()
    )

    stmt = (
        select(
            Conversation.id.label("id"),
            Conversation.created_at,
            func.array_agg(Participant.user_id).label("participants")
        )
        .join(Participant, Conversation.id == Participant.conversation_id)
        .where(Conversation.id.in_(subq))
        .group_by(Conversation.id, Conversation.created_at)
    )

    result = await db.execute(stmt)
    return result.mappings().all()


async def send_messages(
        db: AsyncSession,
        sender_id: int,
        conversation_id: int,
        text: str
):
    result = await db.execute(
        select(Conversation)
        .where(Conversation.id == conversation_id)
    )
    conversation = result.scalar_one_or_none()
    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversations not found"
        )


    message = Message(
        text=text,
        sender_id=sender_id,
        conversation_id=conversation_id,
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message


async def get_messages(
        db: AsyncSession,
        conversation_id: int,
        current_user_id: int,
        limit: int = 100
):
    await db.execute(
        update(Message)
        .where(
            Message.conversation_id == conversation_id,
            Message.sender_id != current_user_id,
            Message.is_read == False
        )
        .values(is_read=True)
    )
    await db.commit()

    messages = await db.execute(
        select(Message)
        .options(selectinload(Message.sender))
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )

    messages = messages.scalars().all()

    return [
        {
            "id": m.id,
            "text": m.text,
            "sender": {
                "id": m.sender.id,
                "full_name": m.sender.full_name,
                "username": m.sender.username
            },
            "created_at": m.created_at,
            "is_read": m.is_read,
        }
        for m in messages
    ]
