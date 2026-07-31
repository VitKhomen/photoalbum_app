from slugify import slugify

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app import models, schemas


# --------- Albums ---------

async def generate_unique_slug(session: AsyncSession, title: str, album_id: int | None = None) -> str:
    base_slug = slugify(title) or "album"
    slug = base_slug
    counter = 1
    while True:
        stmt = select(models.Album.id).where(models.Album.slug == slug)

        if album_id is not None:
            stmt = stmt.where(models.Album.id != album_id)

        exists = await session.scalar(stmt)

        if not exists:
            return slug

        counter += 1
        slug = f"{base_slug}-{counter}"


async def list_albums(session: AsyncSession) -> list[models.Album]:
    stmt = (
        select(models.Album)
        .options(selectinload(models.Album.cover_photo))
        .order_by(models.Album.order.asc(), models.Album.id.asc())
    )
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_album_by_id(session: AsyncSession, album_id: int) -> models.Album | None:
    stmt = (
        select(models.Album)
        .options(
            selectinload(models.Album.photos),
            selectinload(models.Album.cover_photo),
        )
        .where(models.Album.id == album_id)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_album_by_slug(session: AsyncSession, slug: str) -> models.Album | None:
    stmt = (
        select(models.Album)
        .options(
            selectinload(models.Album.photos),
            selectinload(models.Album.cover_photo),
        )
        .where(models.Album.slug == slug)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def count_photos(session: AsyncSession, album_id: int) -> int:
    stmt = select(func.count(models.Photo.id)).where(
        models.Photo.album_id == album_id
    )
    return await session.scalar(stmt) or 0


async def create_album(
    session: AsyncSession,
    data: schemas.AlbumCreate,
) -> models.Album:
    raw_slug = data.slug.strip() if data.slug else None
    base = slugify(raw_slug) if raw_slug else data.title
    slug = await generate_unique_slug(session, base)

    album = models.Album(
        title=data.title,
        description=data.description,
        order=data.order,
        slug=slug,
    )
    session.add(album)
    await session.commit()
    await session.refresh(album)
    return album


async def update_album(
    session: AsyncSession,
    album: models.Album,
    data: schemas.AlbumUpdate,
) -> models.Album:
    if data.title is not None:
        album.title = data.title
    if data.description is not None:
        album.description = data.description
    if data.order is not None:
        album.order = data.order

    if data.slug is not None and data.slug.strip():
        album.slug = await generate_unique_slug(
            session,
            data.slug,
            album_id=album.id,
        )

    if data.cover_photo_id is not None:
        stmt = select(models.Photo).where(
            models.Photo.id == data.cover_photo_id,
            models.Photo.album_id == album.id,
        )
        photo = await session.scalar(stmt)
        if photo is not None:
            album.cover_photo_id = photo.id

    await session.commit()
    await session.refresh(album)
    return album


async def delete_album(session: AsyncSession, album: models.Album) -> None:
    session.delete(album)
    await session.commit()


# --------- Photos ---------

async def get_photo(session: AsyncSession, photo_id: int) -> models.Photo | None:
    stmt = select(models.Photo).where(models.Photo.id == photo_id)
    return await session.scalar(stmt)


async def next_photo_order(session: AsyncSession, album_id: int) -> int:
    stmt = select(func.max(models.Photo.order)).where(
        models.Photo.album_id == album_id
    )
    max_order = await session.scalar(stmt)
    return (max_order or 0) + 1


async def create_photo(
    session: AsyncSession,
    album_id: int,
    file_key: str,
    url: str,
    width: int | None,
    height: int | None,
) -> models.Photo:
    photo = models.Photo(
        album_id=album_id,
        file_key=file_key,
        url=url,
        width=width,
        height=height,
        order=await next_photo_order(session, album_id),
    )
    session.add(photo)
    await session.commit()
    await session.refresh(photo)

    # якщо в альбому ще немає обкладинки — ставимо це фото
    album = await session.get(models.Album, album_id)
    if album is not None and album.cover_photo_id is None:
        album.cover_photo_id = photo.id
        await session.commit()

    return photo


async def delete_photo(session: AsyncSession, photo: models.Photo) -> None:
    album_id = photo.album_id

    album = await session.get(models.Album, album_id)
    was_cover = album is not None and album.cover_photo_id == photo.id

    if was_cover and album is not None:
        album.cover_photo_id = None
        await session.flush()  # щоб FK не блокував delete

    await session.delete(photo)
    await session.commit()

    if was_cover and album is not None:
        stmt = (
            select(models.Photo)
            .where(models.Photo.album_id == album_id)
            .order_by(models.Photo.order.asc())
            .limit(1)
        )
        new_cover = await session.scalar(stmt)
        if new_cover is not None:
            album.cover_photo_id = new_cover.id
            await session.commit()


async def reorder_photos(
    session: AsyncSession,
    album_id: int,
    items: list[schemas.PhotoOrderItem],
) -> None:
    ids = [item.id for item in items]
    stmt = select(models.Photo).where(
        models.Photo.album_id == album_id,
        models.Photo.id.in_(ids),
    )
    result = await session.execute(stmt)
    photos_by_id = {p.id: p for p in result.scalars().all()}

    for item in items:
        photo = photos_by_id.get(item.id)
        if photo is not None:
            photo.order = item.order

    await session.commit()
