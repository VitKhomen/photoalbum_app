from fastapi import APIRouter, HTTPException

from app import crud, schemas
from app.database import SessionDep

router = APIRouter(prefix="/api/albums", tags=["public"])


@router.get("", response_model=list[schemas.AlbumListItem])
async def get_albums(db: SessionDep):
    """Список усіх альбомів по черзі (для головної сторінки)."""
    albums = await crud.list_albums(db)
    result = []
    for album in albums:
        item = schemas.AlbumListItem.model_validate(album)
        item.photos_count = await crud.count_photos(db, album.id)
        result.append(item)
    return result


@router.get("/{slug}", response_model=schemas.AlbumDetail)
async def get_album(slug: str, db: SessionDep):
    """Один альбом з усіма фото (для повноекранного перегляду/свайпу)."""
    album = await crud.get_album_by_slug(db, slug)
    if not album:
        raise HTTPException(status_code=404, detail="Альбом не знайдено")
    return album
