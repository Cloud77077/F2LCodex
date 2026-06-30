from datetime import datetime, timedelta, timezone
from pathlib import Path
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import get_settings
from app.models import StoredFile
from app.storage.local import LocalStorage
from app.storage.s3 import S3Storage
from app.utils.security import generate_token, token_hash

settings = get_settings()

def get_storage():
    if settings.storage_backend.lower() == "s3":
        if not settings.s3_bucket:
            raise RuntimeError("S3_BUCKET is required for S3 storage")
        return S3Storage(settings.s3_bucket, settings.s3_endpoint_url, settings.s3_region, settings.s3_access_key_id, settings.s3_secret_access_key)
    return LocalStorage(settings.local_storage_path)

storage = get_storage()

def expiry_from_hours(hours: int | None = None):
    h = settings.default_link_ttl_hours if hours is None else hours
    return None if h == 0 else datetime.now(timezone.utc) + timedelta(hours=h)

async def create_file_record(session: AsyncSession, source: Path, original_name: str, mime_type: str, size: int, telegram_file_id: str | None = None, telegram_unique_id: str | None = None):
    if settings.max_file_size_bytes and size > settings.max_file_size_bytes:
        raise ValueError("file exceeds MAX_FILE_SIZE_BYTES")
    token = generate_token()
    key = f"{token_hash(token)[:2]}/{token_hash(token)}"
    await storage.save(Path(source), key)
    row = StoredFile(token_hash=token_hash(token), storage_key=key, original_name=original_name, mime_type=mime_type, size=size, telegram_file_id=telegram_file_id, telegram_unique_id=telegram_unique_id, expires_at=expiry_from_hours())
    session.add(row); await session.commit(); await session.refresh(row)
    return token, row

async def get_file_by_token(session: AsyncSession, token: str) -> StoredFile | None:
    row = (await session.execute(select(StoredFile).where(StoredFile.token_hash == token_hash(token)))).scalar_one_or_none()
    if not row or row.revoked: return None
    if row.expires_at and row.expires_at <= datetime.now(timezone.utc): return None
    return row
