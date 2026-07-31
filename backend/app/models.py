from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, String, Text, func, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Album(Base):
    __tablename__ = "albums"

    # id має бути init=False - його генерує база, а не той, хто створює обʼєкт
    id: Mapped[int] = mapped_column(primary_key=True, init=False)

    # обовʼязкові поля (без default) - ідуть ПЕРШИМИ серед init=True полів,
    # інакше dataclass впаде з "non-default argument follows default argument"
    title: Mapped[str] = mapped_column(String(255))
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)

    # опційні поля (є default) - можуть йти після обовʼязкових
    description: Mapped[Optional[str]] = mapped_column(Text, default=None)
    order: Mapped[int] = mapped_column(default=0, index=True)

    # обкладинка альбому - самопосилання на photos.id. Заповнюється ПІСЛЯ
    # створення альбому (коли зʼявиться перше фото), тому init=False.
    cover_photo_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("photos.id", use_alter=True, name="fk_album_cover_photo"),
        default=None,
        init=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        init=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        init=False
    )

    # relationship-поля завжди init=False - їх не передають у конструктор,
    # ними керує сама ORM (через album_id / cover_photo_id)
    photos: Mapped[list["Photo"]] = relationship(
        back_populates="album",
        cascade="all, delete-orphan",
        foreign_keys="Photo.album_id",
        order_by="Photo.order",
        default_factory=list,
        init=False,
    )
    cover_photo: Mapped[Optional["Photo"]] = relationship(
        foreign_keys=[cover_photo_id],
        post_update=True,
        default=None,
        init=False,
    )


class Photo(Base):
    __tablename__ = "photos"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)

    # обовʼязкові (без default) - першими
    album_id: Mapped[int] = mapped_column(
        ForeignKey("albums.id", ondelete="CASCADE"), index=True
    )
    # ключ файлу в бакеті R2 (потрібен для видалення файлу зі сховища)
    file_key: Mapped[str] = mapped_column(String(500))
    # публічний URL для показу на сайті (будуємо один раз при завантаженні)
    url: Mapped[str] = mapped_column(String(1000))

    # опційні
    width: Mapped[Optional[int]] = mapped_column(default=None)
    height: Mapped[Optional[int]] = mapped_column(default=None)
    # порядок фото всередині альбому (для гортання/свайпу по черзі)
    order: Mapped[int] = mapped_column(default=0, index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        init=False,
    )

    album: Mapped["Album"] = relationship(
        back_populates="photos",
        foreign_keys=[album_id],
        init=False,
    )
