from pydantic import BaseModel, ConfigDict
from datetime import datetime
from schemas.user import UserRead


class FriendshipBase(BaseModel):
    friend_id: int


class FriendshipCreate(FriendshipBase):
    pass


class FriendshipOut(FriendshipBase):
    id: int
    user_id: int
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class FriendshipStatusUpdate(BaseModel):
    status: str


class UserWithFriends(UserRead):
    friends: list[UserRead] = []
    pending_requests: list[UserRead] = []

    model_config = ConfigDict(from_attributes=True)