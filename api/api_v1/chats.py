from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_
import json

from schemas.chat import ConversationOut, MessageOut, MessageCreate, MessageOut_get
from models.user import User
from models.chat import Participant
from core.security import get_current_user
from core.database import get_async_session
from crud.chat import create_conversation, get_user_conversations, send_messages, get_messages

router = APIRouter(tags=["chats"])


@router.post("/conversations/", response_model=ConversationOut)
async def create_new_conversation(
        participants_ids: List[int],
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_async_session),
):
    if current_user.id not in participants_ids:
        participants_ids.append(current_user.id)

    if len(participants_ids) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Need at least 2 users"
        )

    result = await db.execute(
        select(User.id)
        .where(User.id.in_(participants_ids))
    )
    existing_ids = set(result.scalars().all())

    missing_ids = set(participants_ids) - existing_ids
    if missing_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Users with IDs {missing_ids} do not exist"
        )

    return await create_conversation(db, participants_ids)


@router.get("/conversations/", response_model=List[ConversationOut])
async def get_my_conversations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session),
):
    raw = await get_user_conversations(db, current_user.id)

    return [
        ConversationOut(
            id=conv["id"],
            created_at=conv["created_at"],
            participants=conv["participants"],
        )
        for conv in raw
    ]


@router.post("/messages", response_model=MessageOut)
async def send_new_message(
        message: MessageCreate,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_async_session),
):
    return await send_messages(db, current_user.id, message.conversation_id, message.text)


@router.get("/conversations/{conversation_id}/messages/", response_model=List[MessageOut_get])
async def get_conversation_messages(
        conversation_id: int,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_async_session),
):
    participants = await db.execute(
        select(Participant)
        .where(and_(
            Participant.conversation_id == conversation_id,
            Participant.user_id == current_user.id
        ))
    )
    if not participants.scalar():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a conversation participant"
        )
    return await get_messages(db, conversation_id, current_user.id)


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_personal_message(self, message: str, user_id: int):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(message)


manager = ConnectionManager()

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(
        websocket: WebSocket,
        user_id: int
):
    await manager.connect(user_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
    except WebSocketDisconnect:
        manager.disconnect(user_id)