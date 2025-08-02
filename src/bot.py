from aiogram import Bot, Dispatcher, types
from aiogram.utils.i18n import I18n

from src.storage.redis import get_redis_storage

from .core import settings
from .middlewares.i18n import CustomI18nMiddleware
from .handlers import start, documents

from .handlers.conversion import images_to_pdf, pdf_to_image, pdf_to_word, word_to_pdf

i18n = I18n(path="src/locales", default_locale="en", domain="messages")


dispatcher = Dispatcher(storage=get_redis_storage())

dispatcher.message.middleware(CustomI18nMiddleware(i18n=i18n))

dispatcher.include_router(start.router)
dispatcher.include_router(documents.router)

dispatcher.include_router(images_to_pdf.router)
dispatcher.include_router(pdf_to_image.router)
dispatcher.include_router(pdf_to_word.router)
dispatcher.include_router(word_to_pdf.router)


async def feed_update(update: dict):
    bot = Bot(token=settings.BOT_TOKEN)

    try:
        aiogram_update = types.Update(**update)

        await dispatcher.feed_update(bot=bot, update=aiogram_update)
    finally:
        await bot.session.close()
