import json
from typing import Dict, Any, Callable, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select
from app.models.user import User
from app.core.database import async_session_maker


class LanguageMiddleware(BaseMiddleware):
    def __init__(self):
        self.locales = {}
        self.load_locales()

    def load_locales(self):
        languages = ["en", "uz", "ru"]
        for lang in languages:
            try:
                with open(f"app/locales/{lang}.json", "r", encoding="utf-8") as f:
                    self.locales[lang] = json.load(f)
            except FileNotFoundError:
                print(f"Locale file for {lang} not found")

    async def __call__(self, handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]], event: Message | CallbackQuery, data: Dict[str, Any]) -> Any:
        user_id = event.from_user.id

        # Get user language from database
        async with async_session_maker() as session:
            result = await session.execute(select(User).where(User.telegram_id == user_id))
            user = result.scalar_one_or_none()

            if user:
                lang = user.language
            else:
                lang = "en"  # Default language

        # Add localization function to data
        data["_"] = lambda key, **kwargs: self.get_text(lang, key, **kwargs)
        data["lang"] = lang

        return await handler(event, data)

    def get_text(self, lang: str, key: str, **kwargs) -> str:
        if lang not in self.locales:
            lang = "en"

        text = self.locales[lang].get(key, key)

        if kwargs:
            try:
                text = text.format(**kwargs)
            except KeyError:
                pass

        return text
