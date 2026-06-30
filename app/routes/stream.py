from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.file_store import get_file_by_token
from app.utils.human import human_bytes

templates = Jinja2Templates(directory="app/templates")
router = APIRouter()

@router.get("/s/{token}")
async def stream_page(token: str, request: Request, session: AsyncSession = Depends(get_session)):
    row = await get_file_by_token(session, token)
    if not row: raise HTTPException(404, "file not found or expired")
    return templates.TemplateResponse("stream.html", {"request": request, "file": row, "token": token, "size": human_bytes(row.size)})
