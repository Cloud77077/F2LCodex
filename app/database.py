import os
from collections.abc import AsyncIterator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.config import get_settings
from app.models import Base

settings = get_settings()
if settings.database_url.startswith("sqlite"):
    db_path = settings.database_url.split("///")[-1]
    if db_path and db_path != ":memory:":
        os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
engine = create_async_engine(settings.database_url, future=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_session() -> AsyncIterator[AsyncSession]:
    async with SessionLocal() as session:
        yield session
