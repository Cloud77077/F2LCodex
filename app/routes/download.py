from urllib.parse import quote
from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import get_settings
from app.database import get_session
from app.file_store import get_file_by_token, storage
from app.utils.ranges import parse_range_header, content_range

router = APIRouter()

@router.get("/d/{token}")
async def download(token: str, request: Request, range: str | None = Header(None), session: AsyncSession = Depends(get_session)):
    row = await get_file_by_token(session, token)
    if not row: raise HTTPException(404, "file not found or expired")
    settings = get_settings(); br = None
    try: br = parse_range_header(range, row.size)
    except ValueError: raise HTTPException(400, "invalid Range header")
    except IndexError: return Response(status_code=416, headers={"Content-Range": f"bytes */{row.size}"})
    headers = {"Accept-Ranges": "bytes", "Content-Disposition": f"attachment; filename*=UTF-8''{quote(row.original_name)}"}
    if settings.use_x_accel_redirect and br is None and storage.local_path(row.storage_key):
        headers.update({"X-Accel-Redirect": settings.x_accel_prefix.rstrip("/") + "/" + row.storage_key, "Content-Type": row.mime_type})
        return Response(headers=headers)
    status = 206 if br else 200; start = br.start if br else 0; end = br.end if br else None
    headers["Content-Length"] = str((br.length if br else row.size))
    if br: headers["Content-Range"] = content_range(br, row.size)
    return StreamingResponse(storage.open(row.storage_key, start, end), status_code=status, media_type=row.mime_type, headers=headers)
