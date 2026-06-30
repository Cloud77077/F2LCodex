import os, tempfile
from aiogram import Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.types import Message
from app.config import get_settings
from app.database import SessionLocal
from app.file_store import create_file_record
from app.telegram_client import make_bot
from app.utils.mime import guess_mime
from app.utils.human import human_bytes, human_ttl

router = Router()

@router.message(Command("start", "help"))
async def start(message: Message):
    await message.answer("Send me a document, video, audio, photo, or voice message and I will return a secure download/streaming link.")

@router.message(Command("limits"))
async def limits(message: Message):
    s = get_settings()
    limit = "no app-defined limit" if s.max_file_size_bytes == 0 else human_bytes(s.max_file_size_bytes)
    await message.answer(f"Max file size: {limit}\nDefault link lifetime: {human_ttl(s.default_link_ttl_hours)}")

@router.message(F.document | F.video | F.audio | F.photo | F.voice)
async def receive_file(message: Message):
    s = get_settings(); bot = make_bot()
    obj = message.document or message.video or message.audio or message.voice or (message.photo[-1] if message.photo else None)
    if obj is None: return
    size = getattr(obj, "file_size", 0) or 0
    if s.max_file_size_bytes and size > s.max_file_size_bytes:
        await message.answer("File is larger than this bot allows."); return
    name = getattr(obj, "file_name", None) or f"telegram-{obj.file_unique_id}"
    mime = getattr(obj, "mime_type", None) or guess_mime(name)
    with tempfile.TemporaryDirectory() as td:
        dest = os.path.join(td, name)
        await bot.download(obj.file_id, destination=dest)
        async with SessionLocal() as session:
            token, row = await create_file_record(session, os.path.abspath(dest), name, mime, os.path.getsize(dest), obj.file_id, obj.file_unique_id)
    url = s.public_base_url.rstrip("/") + f"/d/{token}"
    await message.answer(f"Ready: {url}\nStream page: {s.public_base_url.rstrip('/')}/s/{token}")

def build_dispatcher() -> Dispatcher:
    dp = Dispatcher(); dp.include_router(router); return dp
