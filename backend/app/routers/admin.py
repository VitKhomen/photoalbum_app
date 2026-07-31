import io

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from PIL import Image

from app import crud, schemas
from app.database import SessionDep
from app.dependencies import get_current_admin
from app.security import authenticate_admin, create_access_token
from app.storage import build_object_key, upload_fileobj, delete_object

router = APIRouter(prefix="/api/admin", tags=["admin"])

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}


# --------- Auth ---------

@router.post("/login", response_model=schemas.Token)
def login(data: schemas.LoginRequest):
    if not authenticate_admin(data.username, data.password):
        raise HTTPException(
            status_code=401, detail="Невірний логін або пароль")
    token = create_access_token(subject=data.username)
    return schemas.Token(access_token=token)


# --------- Albums (CRUD, тільки для адміна) ---------

@router.post("/albums", response_model=schemas.AlbumDetail)
async def create_album(
    data: schemas.AlbumCreate,
    db: SessionDep,
    _admin: str = Depends(get_current_admin),
):
    album = await crud.create_album(db, data)
    return album


@router.put("/albums/{album_id}", response_model=schemas.AlbumDetail)
async def update_album(
    album_id: int,
    data: schemas.AlbumUpdate,
    db: SessionDep,
    _admin: str = Depends(get_current_admin),
):
    album = await crud.get_album_by_id(db, album_id)
    if not album:
        raise HTTPException(status_code=404, detail="Альбом не знайдено")
    return await crud.update_album(db, album, data)


@router.delete("/albums/{album_id}", status_code=204)
async def delete_album(
    album_id: int,
    db: SessionDep,
    _admin: str = Depends(get_current_admin),
):
    album = await crud.get_album_by_id(db, album_id)
    if not album:
        raise HTTPException(status_code=404, detail="Альбом не знайдено")

    # видаляємо всі файли з R2, потім сам альбом (каскадом видаляться Photo-записи)
    for photo in album.photos:
        await delete_object(photo.file_key)
    await crud.delete_album(db, album)


# --------- Photos (завантаження в R2, тільки для адміна) ---------

@router.post("/albums/{album_id}/photos", response_model=schemas.PhotoOut)
async def upload_photo(
    album_id: int,
    db: SessionDep,
    file: UploadFile = File(...),
    _admin: str = Depends(get_current_admin),
):
    album = await crud.get_album_by_id(db, album_id)
    if not album:
        raise HTTPException(status_code=404, detail="Альбом не знайдено")

    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Дозволені лише зображення: jpeg, png, webp, gif",
        )

    raw_bytes = await file.read()

    # дізнаємось розміри зображення (потрібно фронтенду для верстки без "стрибків")
    width, height = None, None
    try:
        with Image.open(io.BytesIO(raw_bytes)) as img:
            width, height = img.size
    except Exception:
        pass

    key = build_object_key(album.slug, file.filename or "photo")
    url = await upload_fileobj(io.BytesIO(raw_bytes), key,
                               content_type=file.content_type)

    photo = await crud.create_photo(
        db, album_id=album.id, file_key=key, url=url, width=width, height=height
    )
    return photo


@router.delete("/photos/{photo_id}", status_code=204)
async def delete_photo(
    photo_id: int,
    db: SessionDep,
    _admin: str = Depends(get_current_admin),
):
    photo = await crud.get_photo(db, photo_id)
    if not photo:
        raise HTTPException(status_code=404, detail="Фото не знайдено")

    await delete_object(photo.file_key)
    await crud.delete_photo(db, photo)


@router.put("/albums/{album_id}/photos/reorder", status_code=204)
async def reorder_photos(
    album_id: int,
    data: schemas.PhotoReorderRequest,
    db: SessionDep,
    _admin: str = Depends(get_current_admin),
):
    album = await crud.get_album_by_id(db, album_id)
    if not album:
        raise HTTPException(status_code=404, detail="Альбом не знайдено")
    await crud.reorder_photos(db, album_id, data.items)
