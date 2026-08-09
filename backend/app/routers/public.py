from fastapi import APIRouter, HTTPException, Response

from app import crud, schemas
from app.database import SessionDep

router = APIRouter(prefix="/api/albums", tags=["public"])

PUBLIC_CACHE_CONTROL = "public, max-age=30"


@router.get("", response_model=list[schemas.AlbumListItem])
async def get_albums(db: SessionDep, response: Response):
    """Список усіх альбомів по черзі (для головної сторінки)."""
    response.headers["Cache-Control"] = PUBLIC_CACHE_CONTROL
    albums = await crud.list_albums(db)
    result = []
    for album in albums:
        item = schemas.AlbumListItem.model_validate(album)
        item.photos_count = await crud.count_photos(db, album.id)
        result.append(item)
    return result


@router.get("/{slug}", response_model=schemas.AlbumDetail)
async def get_album(slug: str, db: SessionDep, response: Response):
    """Один альбом з усіма фото (для повноекранного перегляду/свайпу)."""
    response.headers["Cache-Control"] = PUBLIC_CACHE_CONTROL
    album = await crud.get_album_by_slug(db, slug)
    if not album:
        raise HTTPException(status_code=404, detail="Альбом не знайдено")
    return album
