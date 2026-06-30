from aiogram import Bot
from app.config import get_settings

def make_bot() -> Bot:
    settings = get_settings()
    kwargs = {}
    if settings.bot_api_base_url:
        from aiogram.client.telegram import TelegramAPIServer
        from aiogram.client.session.aiohttp import AiohttpSession
        kwargs["session"] = AiohttpSession(api=TelegramAPIServer.from_base(settings.bot_api_base_url, is_local=True))
    return Bot(token=settings.bot_token, **kwargs)
