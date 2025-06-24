from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional, List
from fastapi import UploadFile


class MediaBase(BaseModel):
    file_url: str
    file_type: str
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    thumbnail_url: Optional[str] = None


class MediaCreate(MediaBase):
    pass


class PostBase(BaseModel):
    title: str
    content: str
    media: List[MediaCreate] = Field(default_factory=list)


class Media(MediaBase):
    id: int
    post_id: int

    model_config = ConfigDict(from_attributes=True)


class PostCreate(PostBase):
    pass


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    media: Optional[List[Media]] = None


class Post(BaseModel):
    id: int
    title: str
    content: str
    author_id: int
    created_at: datetime
    updated_at: datetime
    media: List[Media] = []

    model_config = ConfigDict(from_attributes=True)