from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class ProfileBase(BaseModel):
    full_name: Optional[str]
    bio: Optional[str]
    avatar_url: Optional[str]

class ProfileCreate(ProfileBase):
    pass

class ProfileUpdate(ProfileBase):
    pass

class ProfileOut(ProfileBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

