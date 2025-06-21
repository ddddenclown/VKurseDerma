from sqlalchemy import select, and_, func, exists
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from models.chat import Conversation, Participant, Message


async def create_conversation(
        db: AsyncSession,
        user_ids: List[int],
):
    unique_user_ids = list(dict.fromkeys(user_ids))

    conv = Conversation()
    db.add(conv)
    await db.flush()

    for user_id in user_ids:
        participant = Participant(user_id=user_id, conversation_id = conv.id)
        db.add(participant)

    await db.commit()
    return conv


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
        limit: int = 100
):
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    return result.scalars().all()
