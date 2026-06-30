from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from aiogram.types import Update
from app.config import get_settings
from app.database import init_db
from app.bot import build_dispatcher
from app.telegram_client import make_bot
from app.routes import api, download, health, stream

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(title="F2LCodex", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(health.router); app.include_router(download.router); app.include_router(stream.router); app.include_router(api.router)

@app.post(get_settings().webhook_path)
async def telegram_webhook(request: Request):
    dp = build_dispatcher(); bot = make_bot()
    update = Update.model_validate(await request.json(), context={"bot": bot})
    await dp.feed_update(bot, update)
    return {"ok": True}

@app.exception_handler(404)
async def not_found(request: Request, exc):
    from fastapi.templating import Jinja2Templates
    return Jinja2Templates(directory="app/templates").TemplateResponse("error.html", {"request": request, "message": "Not found"}, status_code=404)
