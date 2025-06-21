from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional

class MessageCreate(BaseModel):
    text: str
    conversation_id: int


class MessageOut(BaseModel):
    id: int
    text: str
    sender_id: int
    created_at: datetime
    is_read: bool


class ConversationOut(BaseModel):
    id: int
    created_at: datetime
    participants: List[int] = []


class ConversationWithMessages(BaseModel):
    id: int
    participants: List[int]
    messages: List[MessageOut]