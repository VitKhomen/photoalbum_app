from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# --------- Photo ---------

class PhotoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    album_id: int
    url: str
    width: Optional[int] = None
    height: Optional[int] = None
    order: int
    created_at: datetime


class PhotoOrderItem(BaseModel):
    """Один елемент для масового оновлення порядку фото."""
    id: int
    order: int


class PhotoReorderRequest(BaseModel):
    items: list[PhotoOrderItem]


# --------- Album ---------

class AlbumBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    order: int = 0


class AlbumCreate(AlbumBase):
    slug: Optional[str] = None  # якщо не задано - згенерується з title


class AlbumUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    order: Optional[int] = None
    slug: Optional[str] = None
    cover_photo_id: Optional[int] = None


class AlbumListItem(BaseModel):
    """Легка версія для списку альбомів на головній сторінці."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    slug: str
    description: Optional[str] = None
    order: int
    cover_photo: Optional[PhotoOut] = None
    photos_count: int = 0


class AlbumDetail(BaseModel):
    """Повна версія з усіма фото - для сторінки/секції конкретного альбому."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    slug: str
    description: Optional[str] = None
    order: int
    cover_photo: Optional[PhotoOut] = None
    photos: list[PhotoOut] = []


# --------- Auth ---------

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    username: str
    password: str
