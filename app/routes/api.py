from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.config import get_settings
from app.database import get_session
from app.models import StoredFile

router = APIRouter(prefix="/api")

def require_admin(x_admin_token: str | None = Header(None)):
    token = get_settings().admin_token
    if token and x_admin_token != token: raise HTTPException(401, "invalid admin token")

@router.get("/files", dependencies=[Depends(require_admin)])
async def files(session: AsyncSession = Depends(get_session)):
    rows = (await session.execute(select(StoredFile).order_by(StoredFile.created_at.desc()).limit(100))).scalars()
    return [{"id": r.id, "name": r.original_name, "size": r.size, "mime_type": r.mime_type, "expires_at": r.expires_at} for r in rows]
