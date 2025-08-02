from aiogram.utils.i18n.middleware import I18nMiddleware
from aiogram.types import Message, CallbackQuery, Update


class CustomI18nMiddleware(I18nMiddleware):
    async def get_locale(self, event: Message | CallbackQuery | Update, *args, **kwargs) -> str:
        return getattr(event.from_user, "language_code", "uz")
