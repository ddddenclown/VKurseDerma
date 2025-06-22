from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserOut(BaseModel):
    id: int
    full_name: str
    username: str


class UserRead(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class UserWithDetails(UserBase):
    id: int
    email: EmailStr
    username: str

    model_config = ConfigDict(from_attributes=True)


class UserShort(BaseModel):
    id: int
    full_name: str
    username: str


class MessageOut(BaseModel):
    id: int
    text: str
    sender: UserOut
    conversation_id: int
    created_at: datetime
    is_read: bool

    model_config = ConfigDict(from_attributes=True)
