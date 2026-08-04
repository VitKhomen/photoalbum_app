from typing import Annotated

import dj_database_url
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass

from app.config import DATABASE_URL, DEBUG

# dj_database_url розбирає рядок підключення (postgres://user:pass@host:port/name)
# на компоненти. З них будуємо ДВА url:
#   - ASYNC_DATABASE_URL - для самого застосунку (asyncpg-драйвер)
#   - SYNC_DATABASE_URL  - для Alembic-міграцій (psycopg2, простіше з autogenerate)
_db_config = dj_database_url.parse(DATABASE_URL)

ASYNC_DATABASE_URL = (
    f"postgresql+asyncpg://{_db_config['USER']}:{_db_config['PASSWORD']}"
    f"@{_db_config['HOST']}:{_db_config['PORT']}/{_db_config['NAME']}"
)

SYNC_DATABASE_URL = (
    f"postgresql+psycopg2://{_db_config['USER']}:{_db_config['PASSWORD']}"
    f"@{_db_config['HOST']}:{_db_config['PORT']}/{_db_config['NAME']}"
)

engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=DEBUG,          # SQL-запити в консоль лише коли DEBUG=True в .env
    pool_pre_ping=True,  # перевіряє з'єднання перед використанням
    pool_size=10,
    max_overflow=20,
    connect_args={
        # Supabase (і будь-який pgbouncer у transaction-режимі) не підтримує
        # prepared statements, бо з'єднання перевикористовується між запитами
        # неконтрольовано. asyncpg кешує prepared statements за замовчуванням -
        # це і призводить до "prepared statement ... does not exist".
        "statement_cache_size": 0,
    },
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


class Base(MappedAsDataclass, DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_db)]
