from datetime import datetime, timezone
from sqlalchemy import DateTime, Integer, String, BigInteger, Boolean, Text, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

def utcnow() -> datetime:
    return datetime.now(timezone.utc)

class StoredFile(Base):
    __tablename__ = "stored_files"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    token_hash: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    storage_key: Mapped[str] = mapped_column(Text, nullable=False)
    original_name: Mapped[str] = mapped_column(Text, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(255), nullable=False, default="application/octet-stream")
    size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    telegram_file_id: Mapped[str | None] = mapped_column(Text)
    telegram_unique_id: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    downloads: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

Index("ix_stored_files_expires_at", StoredFile.expires_at)
