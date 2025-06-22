from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import List, Optional

from schemas.user import UserOut

class MessageCreate(BaseModel):
    text: str
    conversation_id: int


class MessageOut(BaseModel):
    id: int
    text: str
    sender_id: int
    created_at: datetime
    is_read: bool


class MessageOut_get(BaseModel):
    id: int
    text: str
    sender: UserOut
    created_at: datetime
    is_read: bool

    model_config = ConfigDict(from_attributes=True)


class ConversationOut(BaseModel):
    id: int
    created_at: datetime
    participants: List[int] = []


class ConversationWithMessages(BaseModel):
    id: int
    participants: List[int]
    messages: List[MessageOut]